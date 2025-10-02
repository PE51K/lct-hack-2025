"""
Logging utilities for the application.

Configures the logging settings and provides a logger instance using aiologger
for asynchronous logging.
"""

from __future__ import annotations

import logging
import sys

from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.streams import AsyncStreamHandler

from .settings import settings


async def setup_logger(name: str = "app_logger", level: str | None = None) -> Logger:
    """
    Set up the logging configuration for the application asynchronously.

    Args:
        name (str): The name of the logger. Defaults to "app_logger".
        level (str): The logging level to set. Defaults to value from settings.

    Returns:
        Logger: The configured aiologger instance with custom formatting.
    """
    if level is None:
        level = settings.app.logging.log_level

    # Create aiologger instance
    logger = Logger(name=name)

    # Set level
    logger.level = getattr(logging, level.upper())

    # Create custom formatter with time, level, name, and location
    formatter = Formatter(
        fmt="{asctime} | {levelname} | {name}:{module}:{funcName}:{lineno} - {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    # Add async handler to stdout with custom formatter
    handler = AsyncStreamHandler(stream=sys.stdout, formatter=formatter)
    logger.add_handler(handler)

    return logger


__all__ = ["setup_logger"]
