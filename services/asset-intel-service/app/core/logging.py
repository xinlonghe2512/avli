"""Logging configuration and setup for the application.

Provides structured logging using structlog with support for:

- Human-readable console logging in development.
- JSON console logging in staging/production.
- JSONL file logging in all environments.
- Request-scoped context.
- ASGI correlation IDs.
- Callsite information in development and test environments.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import override

import structlog
from asgi_correlation_id import correlation_id
from structlog.types import Processor
from structlog.typing import EventDict

from app.core.config import Environment, settings

_request_context: ContextVar[dict[str, object] | None] = ContextVar(
    "request_context",
    default=None,
)


def bind_context(**kwargs: object) -> None:
    """Bind values to the current request logging context.

    Args:
        **kwargs: Key-value pairs to add to the logging context.
    """
    current = _request_context.get() or {}
    _request_context.set({**current, **kwargs})


def clear_context() -> None:
    """Clear the current request logging context."""
    _request_context.set(None)


def get_context() -> dict[str, object]:
    """Return the current request logging context."""
    return _request_context.get() or {}


def add_context_to_event_dict(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add request-scoped context to the event dictionary."""
    context = get_context()

    if context:
        event_dict.update(context)

    return event_dict


def add_request_id_to_event_dict(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add the current ASGI correlation ID to the event dictionary."""
    request_id = correlation_id.get()

    if request_id:
        event_dict["request_id"] = request_id

    return event_dict


def add_environment_to_event_dict(
    _logger: object,
    _method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add the application environment to the event dictionary."""
    event_dict["environment"] = settings.ENVIRONMENT.value
    return event_dict


def get_log_file_path() -> Path:
    """Return the current JSONL log file path."""
    environment = settings.ENVIRONMENT.value
    date = datetime.now().strftime("%Y-%m-%d")

    return settings.LOG_DIR / f"{environment}-{date}.jsonl"


class JsonlFileHandler(logging.Handler):
    """Logging handler that writes rendered JSON events to daily JSONL files."""

    def __init__(self) -> None:
        super().__init__()
        self._file_path = get_log_file_path()

        settings.LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _update_file_path(self) -> None:
        """Update the file path when the calendar day changes."""
        current_path = get_log_file_path()

        if current_path != self._file_path:
            self._file_path = current_path

    @override
    def emit(self, record: logging.LogRecord) -> None:
        """Write a rendered JSON log event to the current JSONL file."""
        try:
            self._update_file_path()

            message = record.getMessage()

            # ProcessorFormatter has already rendered the Structlog event
            # into JSON before it reaches this handler.
            if not isinstance(message, str):
                message = json.dumps(
                    message,
                    ensure_ascii=False,
                    default=str,
                )

            with self._file_path.open(
                "a",
                encoding="utf-8",
            ) as file:
                file.write(message)
                file.write("\n")

        except Exception:
            self.handleError(record)


def get_shared_processors(
    include_file_info: bool = True,
) -> list[Processor]:
    """Build processors shared by Structlog and standard logging records."""
    processors: list[Processor] = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_context_to_event_dict,
        add_request_id_to_event_dict,
        add_environment_to_event_dict,
    ]

    if include_file_info:
        processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.PATHNAME,
                }
            )
        )

    return processors


def setup_logging() -> None:
    """Configure Structlog and standard-library logging.

    Development/test environments use human-readable console output.

    Staging/production environments use JSON console output.

    JSONL file logging is enabled in all environments.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    include_file_info = settings.ENVIRONMENT in {
        Environment.DEVELOPMENT,
        Environment.TEST,
    }

    shared_processors = get_shared_processors(
        include_file_info=include_file_info,
    )

    foreign_pre_chain = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(
            fmt="iso",
            utc=True,
        ),
        structlog.processors.format_exc_info,
        add_context_to_event_dict,
        add_request_id_to_event_dict,
        add_environment_to_event_dict,
    ]

    if include_file_info:
        foreign_pre_chain.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.PATHNAME,
                }
            )
        )

    console_renderer: structlog.types.Processor

    if settings.LOG_FORMAT == "console":
        console_renderer = structlog.dev.ConsoleRenderer()
    else:
        console_renderer = structlog.processors.JSONRenderer()

    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=foreign_pre_chain,
        processors=[
            console_renderer,
        ],
    )

    json_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=foreign_pre_chain,
        processors=[
            structlog.processors.JSONRenderer(),
        ],
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    file_handler = JsonlFileHandler()
    file_handler.setLevel(log_level)
    file_handler.setFormatter(json_formatter)

    root_logger = logging.getLogger()

    # Avoid duplicate handlers when setup_logging() is called more than once.
    root_logger.handlers.clear()

    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


setup_logging()

logger = structlog.get_logger()

log_level_name = "DEBUG" if settings.DEBUG else "INFO"

logger.info(
    "logging_initialized",
    log_level=log_level_name,
    log_format=settings.LOG_FORMAT,
    debug=settings.DEBUG,
)
