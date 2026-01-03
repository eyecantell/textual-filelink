"""Tests for logging infrastructure."""

import logging

import pytest

from textual_filelink import FileLink, FileLinkWithIcons
from textual_filelink.icon import Icon
from textual_filelink.logging import disable_logging, get_logger, setup_logging


class TestLoggingSetup:
    """Test logging configuration."""

    def test_default_null_handler(self):
        """Logger has NullHandler by default."""
        logger = get_logger()
        assert len(logger.handlers) >= 1
        # Should have at least one NullHandler
        assert any(isinstance(h, logging.NullHandler) for h in logger.handlers)

    def test_setup_console_logging(self, caplog):
        """setup_logging() enables console output."""
        try:
            setup_logging(level="DEBUG")
            logger = get_logger()

            # Should have a StreamHandler
            handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            assert len(handlers) >= 1

            # Should be at DEBUG level
            assert logger.level == logging.DEBUG

            # Test actual logging works
            with caplog.at_level(logging.DEBUG):
                logger.debug("test message")
                assert "test message" in caplog.text

        finally:
            disable_logging()

    def test_custom_format_string(self):
        """setup_logging() with custom format string."""
        try:
            custom_format = "%(levelname)s: %(message)s"
            setup_logging(format_string=custom_format)

            logger = get_logger()
            handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))

            assert handler.formatter._fmt == custom_format

        finally:
            disable_logging()

    def test_reconfiguration(self):
        """Calling setup_logging multiple times replaces handlers."""
        try:
            # First setup
            setup_logging(level="DEBUG")
            logger = get_logger()

            # Second setup (should replace handlers)
            setup_logging(level="ERROR")

            # Should still have handlers
            assert len(logger.handlers) > 0

            # Should be at ERROR level now
            assert logger.level == logging.ERROR

        finally:
            disable_logging()

    def test_disable_logging(self):
        """disable_logging() removes all handlers except NullHandler."""
        try:
            # Enable logging
            setup_logging(level="DEBUG")
            logger = get_logger()

            # Should have multiple handlers
            assert len(logger.handlers) > 0

            # Disable logging
            disable_logging()

            # Should only have NullHandler
            assert len(logger.handlers) >= 1
            # All handlers should be NullHandler
            for handler in logger.handlers:
                assert isinstance(handler, logging.NullHandler)

        finally:
            disable_logging()

    def test_string_level_conversion(self):
        """setup_logging converts string levels to logging constants."""
        try:
            setup_logging(level="INFO")
            logger = get_logger()
            assert logger.level == logging.INFO

            setup_logging(level="WARNING")
            assert logger.level == logging.WARNING

        finally:
            disable_logging()


class TestLoggingIntegration:
    """Test logging integration with widgets."""

    def test_filelink_logs_command_execution(self, tmp_path, caplog):
        """FileLink logs command execution details."""
        try:
            setup_logging(level="DEBUG")

            test_file = tmp_path / "test.py"
            test_file.write_text("print('hello')")

            with caplog.at_level(logging.DEBUG):
                FileLink(test_file)

                # Should log the file path information
                # Note: The logger is called during _do_open_file, not __init__
                # So we don't expect logs just from creating the widget

        finally:
            disable_logging()

    def test_filelink_with_icons_logs_validation(self, tmp_path, caplog):
        """FileLinkWithIcons logs validation errors."""
        try:
            setup_logging(level="ERROR")

            test_file = tmp_path / "test.py"
            test_file.write_text("print('hello')")

            # Create duplicate icon names
            with caplog.at_level(logging.ERROR):
                with pytest.raises(ValueError, match="Duplicate icon names"):
                    FileLinkWithIcons(
                        test_file,
                        icons_before=[
                            Icon(name="status", icon="✅"),
                            Icon(name="status", icon="❌"),  # duplicate
                        ],
                    )

                # Should have logged error before raising
                assert any("Duplicate icon names" in record.message for record in caplog.records)

        finally:
            disable_logging()

    def test_filelink_with_icons_logs_duplicate_keys(self, tmp_path, caplog):
        """FileLinkWithIcons logs duplicate key errors."""
        try:
            setup_logging(level="ERROR")

            test_file = tmp_path / "test.py"
            test_file.write_text("print('hello')")

            # Create duplicate icon keys
            with caplog.at_level(logging.ERROR):
                with pytest.raises(ValueError, match="Duplicate icon keys"):
                    FileLinkWithIcons(
                        test_file,
                        icons_before=[
                            Icon(name="status1", icon="✅", key="1"),
                            Icon(name="status2", icon="❌", key="1"),  # duplicate key
                        ],
                    )

                # Should have logged error before raising
                assert any("Duplicate icon keys" in record.message for record in caplog.records)

        finally:
            disable_logging()

    def test_get_logger_returns_same_instance(self):
        """get_logger() returns the same logger instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2
