"""Chat-related tasks."""

from celery import Task

from src.worker import worker


@worker.task(
    bind=True,
    base=Task,
    name="chat.generate_summary",
)  # ty: ignore[dynamic-function-decorator-return]
def generate_chat_summary(_self: Task, text: str) -> str:
    """Generate a basic summary of text."""
    if not text:
        return "No content to summarize."

    summary = text[:100].strip()
    if len(text) > 100:
        summary += "..."

    return f"Summary: {summary}"


@worker.task(
    bind=True,
    base=Task,
    name="chat.generate_title",
)  # ty: ignore[dynamic-function-decorator-return]
def generate_chat_title(_self: Task, text: str) -> str:
    """Generate a basic title for text."""
    if not text:
        return "No content to summarize."

    title = text[:100].strip()
    if len(text) > 100:
        title += "..."

    return f"Title: {title}"
