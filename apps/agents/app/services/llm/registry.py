"""LLM model registry with pre-initialized instances."""

from typing import (
    TypedDict,
    Unpack,
)

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter
from pydantic import SecretStr

from app.core.config import settings
from app.core.logging import logger

OPENROUTER_API_KEY = SecretStr(settings.LLM_API_KEY)
OPENAI_API_KEY = SecretStr(settings.LLM_API_KEY)

# Every model here is a reasoning model, and the API rejects the classic sampling
# knobs (`top_p`, `presence_penalty`, `frequency_penalty`) with a 400 once
# `reasoning` is set. Tune quality with `reasoning.effort` instead.


class LLMOverrides(TypedDict, total=False):
    """Supported per-request LLM overrides."""

    temperature: float
    max_tokens: int
    max_retries: int
    timeout: int


class LLMEntry(TypedDict):
    """A registered LLM entry."""

    name: str
    llm: BaseChatModel


class LLMRegistry:
    """Registry of available LLM models with pre-initialized instances.

    This class maintains a list of LLM configurations and provides
    methods to retrieve them by name with optional argument overrides.
    """

    # Ordered by preference: index 0 is the default and the head of the circular
    # fallback chain, so it degrades newest -> cheapest.
    LLMS: list[LLMEntry] = [
        {
            "name": "deepseek-v4-flash-latest",
            "llm": ChatOpenRouter(
                model="~deepseek/deepseek-v4-flash-latest",
                api_key=OPENROUTER_API_KEY,
                max_completion_tokens=settings.LLM_MAX_TOKENS,
                reasoning={"effort": "medium"},
            ),
        },
        {
            "name": "deepseek-v4-flash",
            "llm": ChatOpenRouter(
                model="deepseek/deepseek-v4-flash",
                api_key=OPENROUTER_API_KEY,
                max_completion_tokens=settings.LLM_MAX_TOKENS,
                reasoning={"effort": "medium"},
            ),
        },
        {
            "name": "gpt-5.4",
            "llm": ChatOpenAI(
                model="gpt-5.4",
                api_key=OPENAI_API_KEY,
                max_completion_tokens=settings.LLM_MAX_TOKENS,
                reasoning={"effort": "medium"},
            ),
        },
    ]

    @classmethod
    def get(cls, model_name: str, **kwargs: Unpack[LLMOverrides]) -> BaseChatModel:
        """Get an LLM by name with optional argument overrides.

        When kwargs are provided a fresh ChatOpenAI instance is returned with
        those overrides applied, leaving the shared registry entry untouched.

        Args:
            model_name: Name of the model to retrieve.
            **kwargs: Optional arguments to override default model configuration.

        Returns:
            BaseChatModel instance.

        Raises:
            ValueError: If model_name is not found in LLMS.
        """
        model_entry = next(
            (entry for entry in cls.LLMS if entry["name"] == model_name),
            None,
        )

        if model_entry is None:
            available = ", ".join(cls.get_all_names())
            raise ValueError(
                f"model '{model_name}' not found in registry. "
                f"available models: {available}"
            )

        llm = model_entry["llm"]

        if not kwargs:
            logger.debug(
                "using_default_llm_instance",
                model_name=model_name,
                model=llm.__class__.__name__,
            )
            return llm

        logger.debug(
            "creating_llm_with_custom_args",
            model_name=model_name,
            model=llm.__class__.__name__,
            custom_args=list(kwargs.keys()),
        )

        return llm.model_copy(update=dict(kwargs))

    @classmethod
    def get_all_names(cls) -> list[str]:
        """Return all registered model names in order.

        Returns:
            List of model name strings.
        """
        return [entry["name"] for entry in cls.LLMS]

    @classmethod
    def get_model_at_index(cls, index: int) -> LLMEntry:
        """Return the model entry at a specific index, wrapping to 0 if out of range.

        Args:
            index: Index into LLMS.

        Returns:
            Model entry dict.
        """
        if 0 <= index < len(cls.LLMS):
            return cls.LLMS[index]
        return cls.LLMS[0]
