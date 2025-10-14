"""Structured logging helpers for the workspace."""

from __future__ import annotations

import logging


def get_logger(name: str = "x_runner") -> logging.Logger:
    """Return a namespaced logger configured for console output."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


_LOGGER = get_logger()


def _emit(level: int, *parts: object) -> None:
    message = " ".join(str(part) for part in parts)
    _LOGGER.log(level, message)


def log_info(*parts: object) -> None:
    _emit(logging.INFO, *parts)


def log_error(*parts: object) -> None:
    _emit(logging.ERROR, *parts)


def log_debug(*parts: object) -> None:
    _emit(logging.DEBUG, *parts)


__all__ = ["get_logger", "log_debug", "log_error", "log_info"]
