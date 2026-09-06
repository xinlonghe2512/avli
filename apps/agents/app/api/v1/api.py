"""API v1 router configuration.

This module sets up the main API router and includes all sub-routers for different
endpoints like authentication and chatbot functionality.
"""

from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.chatbot import router as chatbot_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])


@api_router.get("/health")
async def health_check(_request: Request) -> JSONResponse:
    """Health check endpoint.

    Returns:
        dict: Health status information.
    """
    logger.info("health_check_called")
    return JSONResponse(content={"status": "healthy", "version": "1.0.0"})
