"""
Logging configuration for FlowStateAI.

Provides a reusable logger that writes to both console and file with a
consistent format. Designed for Python 3.11 with type hints and docstrings.
"""

from __future__ import annotations

import logging
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "flowstate",
    log_file: str = "flowstate.log",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Create and configure a logger with console and file handlers.

    Args:
        name: Logger name to create or retrieve.
        log_file: Path to the log file. Parent directories are created if missing.
        level: Logging level to apply to the logger and its handlers.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        # Logger already configured; ensure level is up to date.
        for handler in logger.handlers:
            handler.setLevel(level)
        return logger

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # Ensure log directory exists if the file path includes one.
    log_path = Path(log_file)
    if log_path.parent != Path("."):
        log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


__all__ = ["setup_logger", "LOG_FORMAT", "DATE_FORMAT"]

