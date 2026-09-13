from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from app.schemas.graph import GraphState
from app.services.llm import llm_service


class SupervisorDecision(BaseModel):
    """Decision returned by the supervisor."""

    next_agent: Literal["rag", "research"] = Field(
        description=(
            "The specialist that should handle the user's request. "
            "Use 'rag' for questions about the user's documents or knowledge base, "
            "'research' for questions requiring web research, and 'final' when "
            "the request can be answered directly."
        )
    )


SUPERVISOR_PROMPT = """\
You are the supervisor of a multi-agent assistant.

Your job is to route the user's request to the most appropriate specialist.

Available agents:

- rag:
  Use this for questions about uploaded documents, internal documents,
  company knowledge, private knowledge bases, or indexed content.

- research:
  Use this for questions requiring current information from the internet,
  web search, external sources, news, or recent events.

Choose exactly one agent.

Do not answer the user's question yourself.
"""


async def supervisor_node(
    state: GraphState,
    _config: RunnableConfig,
) -> dict[str, str]:
    """Route the current request to the appropriate specialist agent."""

    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        *state.messages,
    ]

    decision = await llm_service.call(
        messages,
        response_format=SupervisorDecision,
    )

    return {
        "next_agent": decision.next_agent,
    }
