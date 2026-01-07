"""Tests for utility functions."""

import pytest

from textual_filelink.utils import command_from_template, format_duration, format_time_ago, sanitize_id


class TestSanitizeId:
    """Tests for sanitize_id() function."""

    def test_sanitize_basic_string(self):
        """Test basic string sanitization."""
        assert sanitize_id("Run Tests") == "run-tests"
        assert sanitize_id("Build Project") == "build-project"

    def test_sanitize_path_forward_slash(self):
        """Test path sanitization with forward slashes."""
        assert sanitize_id("src/main.py") == "src-main-py"
        assert sanitize_id("tests/unit/test_file.py") == "tests-unit-test_file-py"

    def test_sanitize_path_backslash(self):
        """Test path sanitization with backslashes (Windows)."""
        assert sanitize_id("src\\file.py") == "src-file-py"
        assert sanitize_id("C:\\Users\\name\\file.txt") == "c--users-name-file-txt"

    def test_sanitize_special_characters(self):
        """Test sanitization of special characters."""
        assert sanitize_id("Build!") == "build-"
        assert sanitize_id("Test@Project#123") == "test-project-123"
        assert sanitize_id("File (copy).txt") == "file--copy--txt"

    def test_sanitize_already_clean(self):
        """Test sanitization of already-clean IDs."""
        assert sanitize_id("clean-id") == "clean-id"
        assert sanitize_id("my_widget_123") == "my_widget_123"
        assert sanitize_id("simple") == "simple"

    def test_sanitize_unicode_emoji(self):
        """Test sanitization of unicode and emoji characters."""
        assert sanitize_id("test🔥file") == "test-file"
        assert sanitize_id("my_✅_test") == "my_-_test"

    def test_sanitize_multiple_spaces(self):
        """Test sanitization of multiple consecutive spaces."""
        assert sanitize_id("test  file") == "test--file"
        assert sanitize_id("   spaces   ") == "---spaces---"

    def test_sanitize_mixed_separators(self):
        """Test sanitization with mixed separators."""
        assert sanitize_id("path/to\\file name.txt") == "path-to-file-name-txt"

    def test_sanitize_preserves_underscores(self):
        """Test that underscores are preserved."""
        assert sanitize_id("my_test_file") == "my_test_file"
        assert sanitize_id("TEST_CONSTANT") == "test_constant"

    def test_sanitize_preserves_hyphens(self):
        """Test that hyphens are preserved."""
        assert sanitize_id("my-test-file") == "my-test-file"
        assert sanitize_id("dash-separated-words") == "dash-separated-words"

    def test_sanitize_numbers(self):
        """Test sanitization with numbers."""
        assert sanitize_id("test123") == "test123"
        assert sanitize_id("123test") == "123test"
        assert sanitize_id("v1.2.3") == "v1-2-3"

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string."""
        assert sanitize_id("") == ""

    def test_sanitize_only_special_chars(self):
        """Test sanitization of string with only special characters."""
        assert sanitize_id("!!!") == "---"
        assert sanitize_id("@#$") == "---"


class TestFormatDuration:
    """Tests for format_duration() function."""

    def test_milliseconds(self):
        """Test millisecond formatting for sub-second durations."""
        assert format_duration(0.5) == "500ms"
        assert format_duration(0.999) == "999ms"
        assert format_duration(0.1) == "100ms"
        assert format_duration(0.001) == "1ms"

    def test_zero(self):
        """Test zero duration."""
        assert format_duration(0.0) == "0ms"

    def test_decimal_seconds(self):
        """Test decimal seconds for 1-60s range."""
        assert format_duration(1.0) == "1.0s"
        assert format_duration(30.5) == "30.5s"
        assert format_duration(59.9) == "59.9s"
        assert format_duration(5.3) == "5.3s"

    def test_minutes_and_seconds(self):
        """Test minutes and seconds formatting."""
        assert format_duration(60) == "1m 0s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(125) == "2m 5s"
        assert format_duration(3599) == "59m 59s"

    def test_hours_and_minutes(self):
        """Test hours and minutes formatting."""
        assert format_duration(3600) == "1h 0m"
        assert format_duration(3661) == "1h 1m"
        assert format_duration(7200) == "2h 0m"
        assert format_duration(7325) == "2h 2m"
        assert format_duration(86399) == "23h 59m"

    def test_days_and_hours(self):
        """Test days and hours formatting."""
        assert format_duration(86400) == "1d 0h"
        assert format_duration(90000) == "1d 1h"
        assert format_duration(172800) == "2d 0h"
        assert format_duration(176400) == "2d 1h"
        assert format_duration(604799) == "6d 23h"

    def test_weeks(self):
        """Test weeks formatting."""
        assert format_duration(604800) == "1w"
        assert format_duration(691200) == "1w 1d"
        assert format_duration(1209600) == "2w"
        assert format_duration(1296000) == "2w 1d"

    def test_large_values(self):
        """Test large time values."""
        assert format_duration(2419200) == "4w"  # 4 weeks
        assert format_duration(2505600) == "4w 1d"  # 4 weeks 1 day

    def test_negative_values(self):
        """Test negative values return empty string."""
        assert format_duration(-1.0) == ""
        assert format_duration(-60) == ""
        assert format_duration(-3600) == ""

    def test_boundary_values(self):
        """Test boundary conditions."""
        assert format_duration(0.999) == "999ms"  # Just under 1s
        assert format_duration(1.0) == "1.0s"  # Exactly 1s
        assert format_duration(59.9) == "59.9s"  # Just under 60s
        assert format_duration(60.0) == "1m 0s"  # Exactly 60s


class TestFormatTimeAgo:
    """Tests for format_time_ago() function."""

    def test_seconds(self):
        """Test seconds formatting."""
        assert format_time_ago(0) == "0s ago"
        assert format_time_ago(5) == "5s ago"
        assert format_time_ago(30) == "30s ago"
        assert format_time_ago(59) == "59s ago"

    def test_minutes(self):
        """Test minutes formatting."""
        assert format_time_ago(60) == "1m ago"
        assert format_time_ago(120) == "2m ago"
        assert format_time_ago(300) == "5m ago"
        assert format_time_ago(3599) == "59m ago"

    def test_hours(self):
        """Test hours formatting."""
        assert format_time_ago(3600) == "1h ago"
        assert format_time_ago(7200) == "2h ago"
        assert format_time_ago(10800) == "3h ago"
        assert format_time_ago(86399) == "23h ago"

    def test_days(self):
        """Test days formatting."""
        assert format_time_ago(86400) == "1d ago"
        assert format_time_ago(172800) == "2d ago"
        assert format_time_ago(259200) == "3d ago"
        assert format_time_ago(604799) == "6d ago"

    def test_weeks(self):
        """Test weeks formatting."""
        assert format_time_ago(604800) == "1w ago"
        assert format_time_ago(1209600) == "2w ago"
        assert format_time_ago(1814400) == "3w ago"

    def test_negative_values(self):
        """Test negative values return empty string."""
        assert format_time_ago(-1) == ""
        assert format_time_ago(-60) == ""
        assert format_time_ago(-3600) == ""

    def test_fractional_seconds(self):
        """Test fractional seconds are truncated."""
        assert format_time_ago(5.5) == "5s ago"
        assert format_time_ago(59.9) == "59s ago"

    def test_boundary_values(self):
        """Test boundary conditions."""
        assert format_time_ago(59) == "59s ago"  # Just under 60s
        assert format_time_ago(60) == "1m ago"  # Exactly 60s
        assert format_time_ago(3599) == "59m ago"  # Just under 60m
        assert format_time_ago(3600) == "1h ago"  # Exactly 60m


class TestCommandFromTemplate:
    """Tests for command_from_template() function."""

    def test_basic_template(self, tmp_path):
        """Test basic template with path variable."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path }}")
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

    def test_template_with_line_column(self, tmp_path):
        """Test template with line and column variables."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path }} {{ line }} {{ column }}")
        result = builder(test_file, 42, 5)
        assert result == ["editor", str(test_file.resolve()), "42", "5"]

    def test_vscode_style_template(self, tmp_path):
        """Test VSCode-style colon-separated template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("code --goto {{ path }}:{{ line }}:{{ column }}")
        result = builder(test_file, 10, 5)
        assert result == ["code", "--goto", f"{test_file.resolve()}:10:5"]

    def test_vim_style_template(self, tmp_path):
        """Test vim-style template with line_plus."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("vim {{ line_plus }} {{ path }}")
        result = builder(test_file, 42, None)
        assert result == ["vim", "+42", str(test_file.resolve())]

    def test_line_plus_none_value(self, tmp_path):
        """Test that line_plus doesn't create bare + when None."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("vim {{ line_plus }} {{ path }}")
        result = builder(test_file, None, None)
        # Should NOT have bare +
        assert result == ["vim", str(test_file.resolve())]

    def test_path_name_variable(self, tmp_path):
        """Test path_name variable extracts filename."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path_name }}")
        result = builder(test_file, None, None)
        assert result == ["editor", "test.py"]

    def test_unknown_variable_raises_error(self):
        """Test that unknown variables raise ValueError."""
        with pytest.raises(ValueError, match="Unknown template variables"):
            command_from_template("editor {{ unknown }} {{ path }}")

    def test_typo_in_variable_caught(self):
        """Test that typos are caught by validation."""
        with pytest.raises(ValueError, match="Unknown template variables"):
            command_from_template("editor {{ pth }} {{ line }}")  # typo: pth instead of path

    def test_whitespace_variations(self, tmp_path):
        """Test that {{ var }} and {{var}} both work."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder1 = command_from_template("editor {{ path }}")
        builder2 = command_from_template("editor {{path}}")

        result1 = builder1(test_file, None, None)
        result2 = builder2(test_file, None, None)
        assert result1 == result2

    def test_quoted_paths_with_spaces(self, tmp_path):
        """Test that quoted paths with spaces stay together."""
        test_file = tmp_path / "my file.py"
        test_file.write_text("test")

        builder = command_from_template('editor "{{ path }}"')
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

    def test_empty_values_handled(self, tmp_path):
        """Test that None values produce empty strings that collapse."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ line }} {{ column }} {{ path }}")
        result = builder(test_file, None, None)
        # shlex.split() collapses whitespace
        assert result == ["editor", str(test_file.resolve())]
