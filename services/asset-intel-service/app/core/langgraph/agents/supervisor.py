""" """

from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import llm_inference_duration_seconds
from app.schemas.graph import GraphState
from app.services.llm import LLMService


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


SUPERVISOR_SYSTEM_MESSAGE = """\
# Role
You are the supervisor of a multi-agent assistant.

# Job
Route the user's request to the most appropriate specialist.

# Available agents
- rag: Use this for questions about uploaded documents, internal documents,
  company knowledge, private knowledge bases, or indexed content.
- research: Use this for questions requiring current information from the internet,
  web search, external sources, news, or recent events.

# Instructions
- Select the most appropriate agent.
- Do not answer the user's question yourself.
- Route the request to exactly one agent.
"""


class SupervisorAgent:
    """Agent that route user requests to the appropriate specialist agent."""

    def __init__(self, llm_service: LLMService) -> None:
        self.llm_service = llm_service

    async def __call__(
        self,
        state: GraphState,
        config: RunnableConfig,
    ) -> dict[str, str]:
        """Route the current request to a specialist agent."""

        thread_id = config.get("configurable", {}).get("thread_id")

        messages = [
            SystemMessage(content=SUPERVISOR_SYSTEM_MESSAGE),
            *state.messages,
        ]

        try:
            with llm_inference_duration_seconds.labels(
                model=settings.LLM_MODEL,
            ).time():
                decision = await self.llm_service.call(
                    messages,
                    response_format=SupervisorDecision,
                )

            logger.info(
                "supervisor_decision_generated",
                session_id=thread_id,
                next_agent=decision.next_agent,
                environment=settings.ENVIRONMENT.value,
            )

            return {
                "next_agent": decision.next_agent,
            }

        except Exception as exc:
            logger.error(
                "supervisor_llm_call_failed",
                session_id=thread_id,
                error=str(exc),
                environment=settings.ENVIRONMENT.value,
            )
            raise
