"""Message/context management utilities for the application."""

from collections.abc import Sequence
from typing import Any, cast

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_core.messages import trim_messages as _trim_messages

from src.core.config import settings
from src.core.logging import logger
from src.core.tokenizer import deepseek_tokenizer
from src.schemas import Message

MessageInput = (
    BaseMessage
    | list[str]
    | tuple[str, str | list[str | dict[str, Any]]]
    | str
    | dict[str, Any]
)


def convert_messages(
    messages: Sequence[Message],
) -> list[AnyMessage]:
    result: list[AnyMessage] = []

    for message in messages:
        if message.role == "user":
            result.append(HumanMessage(content=message.content))
        elif message.role == "assistant":
            result.append(AIMessage(content=message.content))
        elif message.role == "system":
            result.append(SystemMessage(content=message.content))
        else:
            raise ValueError(f"Unsupported message role: {message.role}")

    return result


def extract_text_content(
    content: str | list[str | dict[str, Any]],
) -> str:
    """Extract plain text from an LLM content value.

    Handles both the simple string format and the structured block list
    returned by Responses API models.

    Args:
        content: Raw content from a LangChain BaseMessage.

    Returns:
        Plain text string (empty string when nothing extractable is present).
    """
    if isinstance(content, str):
        return content

    parts: list[str] = []

    for block in content:
        if isinstance(block, str):
            parts.append(block)

        elif isinstance(block, dict):
            if block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)

            elif block.get("type") == "reasoning":
                logger.debug(
                    "reasoning_block_received",
                    reasoning_id=block.get("id"),
                    has_summary=bool(block.get("summary")),
                )

    return "".join(parts)


def process_llm_response(response: BaseMessage) -> BaseMessage:
    """Normalise a raw LLM response so that ``response.content`` is always a plain string, regardless of the provider's content format.

    Args:
        response: The raw response from the LLM.

    Returns:
        The same BaseMessage instance with ``content`` set to a plain string.
    """
    if isinstance(response.content, list):
        response.content = extract_text_content(response.content)
        logger.debug(
            "processed_structured_content",
            content_block_count=len(response.content),
            extracted_length=len(response.content),
        )
    return response


def prepare_messages(
    messages: Sequence[AnyMessage],
    system_prompt: str,
) -> list[AnyMessage]:
    """Prepare the messages for the LLM.

    Args:
        messages (list[Message]): The messages to prepare.
        system_prompt (str): The system prompt to use.

    Returns:
        list[Message]: The prepared messages.
    """
    try:
        trimmed_messages = _trim_messages(
            list(messages),
            strategy="last",
            token_counter=deepseek_tokenizer.count_tokens,
            max_tokens=settings.LLM_CONTEXT_BUDGET,
            start_on="human",
            include_system=False,
            allow_partial=False,
        )

        trimmed_messages = cast(list[AnyMessage], trimmed_messages)

    except ValueError as e:
        # Handle unrecognized content blocks (e.g., reasoning blocks from Response API Models).
        if "Unrecognized content block type" in str(e):
            logger.warning(
                "token_counting_failed_skipping_trim",
                error=str(e),
                message_count=len(messages),
            )
            trimmed_messages = messages
        else:
            raise

    return [
        SystemMessage(content=system_prompt),
        *trimmed_messages,
    ]
