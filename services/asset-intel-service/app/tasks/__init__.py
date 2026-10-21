"""Initialize the chat route Celery tasks."""

from .chat import generate_chat_summary, generate_chat_title

__all__ = ["generate_chat_summary", "generate_chat_title"]
