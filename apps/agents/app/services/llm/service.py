"""LLM service with retries, circular fallback, and optional structured output."""

import asyncio
import logging
from collections.abc import Callable, Sequence
from typing import Any, TypeVar, Unpack, cast, overload

from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from openai import (
    APIError,
    APITimeoutError,
    OpenAIError,
    RateLimitError,
)
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from typing_extensions import TypedDict

from app.core.config import settings
from app.core.logging import logger
from app.services.llm.registry import LLMRegistry

T = TypeVar("T", bound=BaseModel)

type LLMRunnable = Runnable[LanguageModelInput, BaseMessage | BaseModel]
type ToolInput = BaseTool | type[BaseModel] | Callable[..., Any] | dict[str, object]


class ReasoningConfig(TypedDict):
    effort: str


class ModelKwargs(TypedDict, total=False):
    """Keyword arguments supported by LLMRegistry.get."""

    temperature: float
    max_tokens: int
    reasoning: ReasoningConfig
    timeout: int
    max_retries: int


TRANSIENT_ERRORS = (
    RateLimitError,
    APITimeoutError,
    APIError,
    TimeoutError,
)


class LLMService:
    """Service for managing LLM calls with resilient retries and fallback."""

    def __init__(self) -> None:
        """Initialize the service and identify the configured default model index."""
        self._all_names: list[str] = LLMRegistry.get_all_names()
        self._default_model_index: int = 0
        self._default_bound_tools: list[ToolInput] = []

        try:
            self._default_model_index = self._all_names.index(
                settings.LANGGRAPH_LLM_MODEL
            )
            logger.info(
                "llm_service_initialized",
                default_model=settings.LANGGRAPH_LLM_MODEL,
                model_index=self._default_model_index,
                total_models=len(self._all_names),
            )
        except (ValueError, IndexError) as e:
            self._default_model_index = 0
            fallback_name = self._all_names[0] if self._all_names else "none"
            logger.warning(
                "default_model_not_found_using_first",
                requested=settings.LANGGRAPH_LLM_MODEL,
                using=fallback_name,
                error=str(e),
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_llm(
        self,
        model_name: str | None = None,
        **model_kwargs: Unpack[ModelKwargs],
    ) -> BaseChatModel | LLMRunnable:
        """Return a fresh or tool-bound ChatModel instance on demand."""
        name = model_name or (
            self._all_names[self._default_model_index]
            if self._all_names
            else settings.LANGGRAPH_LLM_MODEL
        )
        model: BaseChatModel = LLMRegistry.get(name, **model_kwargs)
        if self._default_bound_tools:
            return model.bind_tools(self._default_bound_tools)
        return model

    @overload
    async def call(
        self,
        messages: LanguageModelInput,
        model_name: str | None = ...,
        response_format: None = ...,
        tools: Sequence[ToolInput] | None = ...,
        **model_kwargs: Unpack[ModelKwargs],
    ) -> BaseMessage: ...

    @overload
    async def call(
        self,
        messages: LanguageModelInput,
        model_name: str | None = ...,
        *,
        response_format: type[T],
        tools: Sequence[ToolInput] | None = ...,
        **model_kwargs: Unpack[ModelKwargs],
    ) -> T: ...

    async def call(
        self,
        messages: LanguageModelInput,
        model_name: str | None = None,
        response_format: type[BaseModel] | None = None,
        tools: Sequence[ToolInput] | None = None,
        **model_kwargs: Unpack[ModelKwargs],
    ) -> BaseMessage | BaseModel:
        """Call LLM with per-request fallback and retries within a strict timeout budget.

        Args:
            messages: Conversation messages to send.
            model_name: Override the model. None starts from the configured default.
            response_format: Optional Pydantic schema for structured output.
            tools: Optional tools to bind per-call. Defaults to pre-bound tools.
            **model_kwargs: Validated model configuration parameters.

        Returns:
            BaseMessage when response_format is None, otherwise a validated
            instance of response_format.

        Raises:
            RuntimeError: When all models fail or the global timeout is exceeded.
            ValueError: If a requested model_name does not exist in LLMRegistry.
        """
        active_tools = list(tools) if tools is not None else self._default_bound_tools

        try:
            return await asyncio.wait_for(
                self._execute_with_fallback(
                    messages=messages,
                    model_name=model_name,
                    response_format=response_format,
                    tools=active_tools,
                    model_kwargs=model_kwargs,
                ),
                timeout=settings.LANGGRAPH_LLM_TOTAL_TIMEOUT,
            )
        except TimeoutError:
            logger.exception(
                "llm_total_timeout_exceeded",
                timeout_seconds=settings.LANGGRAPH_LLM_TOTAL_TIMEOUT,
            )
            raise RuntimeError(
                f"LLM call timed out after {settings.LANGGRAPH_LLM_TOTAL_TIMEOUT}s total budget"
            )

    def bind_tools(self, tools: Sequence[ToolInput]) -> "LLMService":
        """Configure default tools to bind to models during invocation.

        Args:
            tools: Sequence of tools or tool definitions to bind as defaults.

        Returns:
            Self for method chaining.
        """
        self._default_bound_tools = list(tools)
        logger.debug("default_tools_registered_for_llm", tool_count=len(tools))
        return self

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _resolve_model(
        self,
        model_name: str,
        response_format: type[BaseModel] | None,
        tools: list[ToolInput],
        model_kwargs: ModelKwargs,
    ) -> LLMRunnable:
        """Construct or retrieve a configured Runnable without mutating service state."""
        chat_model: BaseChatModel = LLMRegistry.get(model_name, **model_kwargs)

        # 1. Structured output takes precedence (uses chat_model directly)
        if response_format is not None:
            return cast(LLMRunnable, chat_model.with_structured_output(response_format))

        # 2. Tool binding (returns a Runnable)
        if tools:
            return cast(LLMRunnable, chat_model.bind_tools(tools))

        # 3. Base model
        return cast(LLMRunnable, chat_model)

    async def _invoke_with_retry(
        self,
        runnable: LLMRunnable,
        messages: LanguageModelInput,
    ) -> BaseMessage | BaseModel:
        """Execute a single model runnable with transient error retry logic."""
        retryer = AsyncRetrying(
            stop=stop_after_attempt(settings.LANGGRAPH_LLM_MAX_CALL_RETRIES),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(TRANSIENT_ERRORS),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True,
        )

        async for attempt in retryer:
            with attempt:
                return await runnable.ainvoke(messages)

        raise RuntimeError("Retry loop exited unexpectedly without a result")

    async def _execute_with_fallback(
        self,
        messages: LanguageModelInput,
        model_name: str | None,
        response_format: type[BaseModel] | None,
        tools: list[ToolInput],
        model_kwargs: ModelKwargs,
    ) -> BaseMessage | BaseModel:
        """Iterate through registry models on failure without mutating shared state."""
        if not self._all_names:
            raise RuntimeError("LLM Registry has no configured models.")

        if model_name and model_name not in self._all_names:
            raise ValueError(
                f"Model '{model_name}' not found in registry. "
                f"Available models: {', '.join(self._all_names)}"
            )

        start_index = (
            self._all_names.index(model_name)
            if model_name
            else self._default_model_index
        )

        total_models = len(self._all_names)
        last_error: Exception | None = None

        for attempt_num in range(total_models):
            current_index = (start_index + attempt_num) % total_models
            current_model_name = self._all_names[current_index]

            try:
                runnable = self._resolve_model(
                    model_name=current_model_name,
                    response_format=response_format,
                    tools=tools,
                    model_kwargs=model_kwargs,
                )
                return await self._invoke_with_retry(runnable, messages)
            except (OpenAIError, TimeoutError, Exception) as err:
                last_error = err
                logger.warning(
                    "model_call_exhausted_falling_back",
                    model=current_model_name,
                    attempt=attempt_num + 1,
                    total_models=total_models,
                    error=str(err),
                )

        raise RuntimeError(
            f"Failed to get response after trying {total_models} models. "
            f"Last error: {last_error}"
        )


llm_service = LLMService()
