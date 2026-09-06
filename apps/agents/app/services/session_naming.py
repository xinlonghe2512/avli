"""Session auto-naming feature.

On the first message of a new session this module:
  1. Atomically claims the session in Postgres (prevents duplicate LLM calls
     across concurrent requests and multiple uvicorn workers).
  2. Writes a placeholder name derived from the user's message so the session
     always has a sensible name even if the LLM call later fails.
  3. Fires a background asyncio task that calls a fast nano model with
     structured output to generate a proper title and overwrites the placeholder.
"""

import asyncio
from collections.abc import Sequence

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from sqlmodel import (
    Session as DBSession,
)
from sqlmodel import (
    col,
    update,
)

from app.core.logging import logger
from app.core.metrics import session_names_generated_total
from app.core.prompts import SESSION_TITLE_PROMPT
from app.models.session import Session as ChatSession
from app.schemas.chat import Message, SessionTitle
from app.services.database import database_service
from app.services.llm import llm_service

_PLACEHOLDER_MAX = 40

_background_tasks: set[asyncio.Task[None]] = set()


def _build_placeholder(user_message: str) -> str:
    cleaned = " ".join(user_message.split())
    return cleaned[:_PLACEHOLDER_MAX].rstrip() or "New chat"


def _claim_session(session_id: str, placeholder: str) -> bool:
    """Return True iff this caller wins the atomic Postgres claim.

    Executes UPDATE … WHERE name = '' in a single round-trip so exactly one
    concurrent caller receives rowcount == 1.
    """
    with DBSession(database_service.engine) as db:
        stmt = (
            update(ChatSession)
            .where(col(ChatSession.id) == session_id, col(ChatSession.name) == "")
            .values(name=placeholder)
        )
        result = db.exec(stmt)
        db.commit()
        return (result.rowcount or 0) == 1


async def _persist_session_name(session_id: str, user_message: str) -> None:
    try:
        result = await llm_service.call(
            [
                SystemMessage(content=SESSION_TITLE_PROMPT),
                HumanMessage(content=user_message[:500]),
            ],
            model_name="gpt-5.4-nano",
            response_format=SessionTitle,
            reasoning={"effort": "low"},
            max_tokens=32,
            temperature=0.3,
        )
        await database_service.update_session_name(session_id, result.title)
        session_names_generated_total.labels(status="success").inc()
        logger.info("session_name_generated", session_id=session_id, name=result.title)
    except Exception:
        session_names_generated_total.labels(status="error").inc()
        logger.exception("session_name_generation_failed", session_id=session_id)


def _to_langchain_messages(
    messages: Sequence[Message],
) -> list[BaseMessage]:
    """Convert API messages to LangChain messages."""
    result: list[BaseMessage] = []

    for message in messages:
        match message.role:
            case "user":
                result.append(HumanMessage(content=message.content))
            case "assistant":
                result.append(AIMessage(content=message.content))
            case "system":
                result.append(SystemMessage(content=message.content))

    return result


def maybe_name_session(
    session_id: str,
    session_name: str,
    messages: Sequence[Message],
) -> None:
    """Trigger session auto-naming if the session is still unnamed.

    Safe to call from any chat endpoint — concurrent callers for the same
    session are deduplicated by the Postgres claim.
    """
    if session_name:
        return

    langchain_messages = _to_langchain_messages(messages)

    first_user_msg: str | None = next(
        (
            message.content
            for message in langchain_messages
            if isinstance(message, HumanMessage) and isinstance(message.content, str)
        ),
        None,
    )

    if not first_user_msg:
        return

    if _claim_session(
        session_id,
        _build_placeholder(first_user_msg),
    ):
        task = asyncio.create_task(_persist_session_name(session_id, first_user_msg))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
