"""
Utility functions for the Agentic AI application.

Includes logging setup, exception handling, and common utilities.
"""

import json
import logging
import logging.config
from typing import Any, Dict

from ..config import get_config


def setup_logging(name: str = "agentic_ai") -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    config = get_config()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": config.log_level,
                "formatter": "detailed",
                "filename": "logs/agentic_ai.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "root": {
            "level": config.log_level,
            "handlers": ["console", "file"],
        },
    }

    # Only add file handler if in production to avoid log file creation in dev
    if config.env == "production":
        pass  # Use both console and file in production
    else:
        # Only use console handler in development
        logging_config["root"]["handlers"] = ["console"]

    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)


def format_response(
    status: str,
    data: Any = None,
    error: str = None,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Format a standardized response.

    Args:
        status: Response status (success/error/pending)
        data: Response data
        error: Error message if applicable
        metadata: Additional metadata

    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "data": data,
    }

    if error:
        response["error"] = error

    if metadata:
        response["metadata"] = metadata

    return response


def parse_json_safe(json_string: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string.

    Args:
        json_string: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed object or default value
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


class AgenticException(Exception):
    """Base exception for agentic AI errors."""

    pass


class AgentExecutionError(AgenticException):
    """Exception raised when agent execution fails."""

    pass


class TaskExecutionError(AgenticException):
    """Exception raised when task execution fails."""

    pass


class ModelInvocationError(AgenticException):
    """Exception raised when model invocation fails."""

    pass
