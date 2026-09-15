from uuid import uuid4

from asgi_correlation_id import correlation_id
from pydantic import BaseModel, Field


def _get_request_id() -> str:
    """Return the current request's correlation ID, or a fresh UUID as fallback."""
    return correlation_id.get() or str(uuid4())


class BaseResponse(BaseModel):
    """Base response model shared across all endpoints."""

    request_id: str = Field(
        default_factory=_get_request_id,
        description="Unique identifier for this request",
    )
