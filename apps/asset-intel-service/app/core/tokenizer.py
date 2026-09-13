"""Tokenization utilities for LLM context management."""

from collections.abc import Sequence
from typing import Any, Protocol

import tiktoken
from deepseek_tokenizer import ds_token
from langchain_core.messages import BaseMessage

from app.core.config import settings

try:
    _TIKTOKEN_ENCODING = tiktoken.encoding_for_model(settings.LLM_MODEL)
except KeyError:
    _TIKTOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")


MessageInput = (
    BaseMessage
    | list[str]
    | tuple[str, str | list[str | dict[str, Any]]]
    | str
    | dict[str, Any]
)


class Tokenizer(Protocol):
    """Protocol for LLM tokenizers."""

    def count_tokens(
        self,
        messages: Sequence[MessageInput],
    ) -> int:
        """Count tokens for a sequence of messages."""
        ...


class DeepSeekTokenizer(Tokenizer):
    """DeepSeek V4 tokenizer implementation."""

    def count_tokens(
        self,
        messages: Sequence[MessageInput],
    ) -> int:
        """Count DeepSeek V4 tokens locally.

        Uses the DeepSeek V4 community-maintained tokenizer,
        which is appropriate for DeepSeek V4 Flash.

        Args:
            messages: Messages to count.

        Returns:
            Token count for the message contents.
        """
        num_tokens = 0

        for message in messages:
            if isinstance(message, str):
                num_tokens += len(ds_token.encode(message))

            elif isinstance(message, dict):
                for value in message.values():
                    if isinstance(value, str):
                        num_tokens += len(ds_token.encode(value))

            elif isinstance(message, BaseMessage):
                content = message.content

                if isinstance(content, str):
                    num_tokens += len(ds_token.encode(content))

                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, str):
                            num_tokens += len(ds_token.encode(block))

                        elif isinstance(block, dict):
                            text = block.get("text")

                            if isinstance(text, str):
                                num_tokens += len(ds_token.encode(text))

        return num_tokens


class OpenAITokenizer(Tokenizer):
    def count_tokens(
        self,
        messages: Sequence[MessageInput],
    ) -> int:

        num_tokens = 0

        for message in messages:
            # Every message has overhead tokens for role/name
            num_tokens += 4
            if isinstance(message, dict):
                for _, value in message.items():
                    if isinstance(value, str):
                        num_tokens += len(_TIKTOKEN_ENCODING.encode(value))
            elif isinstance(message, BaseMessage):
                content = message.content
                if isinstance(content, str):
                    num_tokens += len(_TIKTOKEN_ENCODING.encode(content))
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, str):
                            num_tokens += len(_TIKTOKEN_ENCODING.encode(block))
                        elif isinstance(block, dict) and "text" in block:
                            num_tokens += len(_TIKTOKEN_ENCODING.encode(block["text"]))
        num_tokens += 2  # every reply is primed with assistant

        return num_tokens


deepseek_tokenizer = DeepSeekTokenizer()
openai_tokenizer = OpenAITokenizer()
