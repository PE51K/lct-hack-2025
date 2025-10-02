"""
Logging utilities for test databases initialization.

Configures logging settings.
"""

import logging
import sys


def setup_logger(name: str = "test_dbs_logger", level: str = "INFO") -> logging.Logger:
    """
    Set up the logging configuration.

    Args:
        name (str): The name of the logger. Defaults to "test_dbs_logger".
        level (str): The logging level to set. Defaults to "INFO".

    Returns:
        logging.Logger: The configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger()


__all__ = ["logger", "setup_logger"]
