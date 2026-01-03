"""Logging infrastructure for textual-filelink.

By default, a NullHandler is attached (library best practice).
Users can enable logging via setup_logging() or standard Python logging.

Example:
    # Quick console debugging
    from textual_filelink import setup_logging
    setup_logging(level="DEBUG")

    # Or use standard Python logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
"""

from __future__ import annotations

import logging
from typing import Literal

_LOGGER_NAME = "textual_filelink"
_logger = logging.getLogger(_LOGGER_NAME)
_logger.addHandler(logging.NullHandler())

_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | int = "DEBUG",
    format_string: str | None = None,
) -> None:
    """Enable console logging for textual-filelink.

    Parameters
    ----------
    level : str or int
        Logging level (e.g., "DEBUG", "INFO", logging.DEBUG). Default: "DEBUG"
    format_string : str | None
        Custom format string. If None, uses default format with timestamp,
        logger name, level, function, line number, and message.

    Examples
    --------
    >>> from textual_filelink import setup_logging
    >>> setup_logging(level="DEBUG")

    >>> setup_logging(level="INFO", format_string="%(levelname)s: %(message)s")

    Notes
    -----
    For file logging or advanced configuration, use Python's standard
    logging module directly.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    # Remove existing handlers (allow reconfiguration)
    disable_logging()

    _logger.setLevel(level)

    # Add console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string or _DEFAULT_FORMAT))
    _logger.addHandler(handler)


def disable_logging() -> None:
    """Remove all handlers except NullHandler.

    This resets the logger to its default state.

    Examples
    --------
    >>> from textual_filelink import setup_logging, disable_logging
    >>> setup_logging()  # Enable logging
    >>> # ... do work ...
    >>> disable_logging()  # Clean up
    """
    for handler in _logger.handlers[:]:
        if not isinstance(handler, logging.NullHandler):
            handler.close()
            _logger.removeHandler(handler)

    if not any(isinstance(h, logging.NullHandler) for h in _logger.handlers):
        _logger.addHandler(logging.NullHandler())


def get_logger() -> logging.Logger:
    """Get the package logger (for internal use by widgets).

    Returns
    -------
    logging.Logger
        The textual_filelink logger instance

    Examples
    --------
    >>> # In a textual_filelink module:
    >>> from textual_filelink.logging import get_logger
    >>> _logger = get_logger()
    >>> _logger.debug("Debug message")
    """
    return _logger
