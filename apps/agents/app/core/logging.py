"""Logging configuration and setup for the application.

This module provides structured logging configuration using structlog,
with environment-specific formatters and handlers. It supports both
console-friendly development logging and JSON-formatted production logging.
"""

import sys

from loguru import logger

# logger.debug("Agent state: {}", state)
# logger.info("Processing request")
# logger.warning("Tool returned no results")
# logger.error("Tool request failed")
# logger.exception("Unexpected agent failure")


def setup_logging() -> None:
    """Configure application-wide logging."""

    # Remove Loguru's default handler
    logger.remove()

    # Add application handler
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
