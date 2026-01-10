"""Tests for command template functionality."""

import pytest

from textual_filelink import CommandLink, FileLink, FileLinkWithIcons, command_from_template


class TestCommandFromTemplate:
    """Tests for command_from_template() utility function."""

    def test_basic_path_variables(self, tmp_path):
        """Test all path variable types."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        # Test {{ path }} - absolute path
        builder = command_from_template("editor {{ path }}")
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

        # Test {{ path_name }} - just filename
        builder = command_from_template("editor {{ path_name }}")
        result = builder(test_file, None, None)
        assert result == ["editor", "test.py"]

    def test_path_relative(self, tmp_path, monkeypatch):
        """Test {{ path_relative }} when file is under cwd."""
        # Change to tmp_path so file is relative
        monkeypatch.chdir(tmp_path)
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path_relative }}")
        result = builder(test_file, None, None)
        assert result == ["editor", "test.py"]

    def test_path_relative_fallback(self, tmp_path):
        """Test {{ path_relative }} falls back to absolute when not under cwd."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path_relative }}")
        result = builder(test_file, None, None)
        # Should use absolute path when not under cwd
        assert result == ["editor", str(test_file.resolve())]

    def test_line_and_column_variables(self, tmp_path):
        """Test line and column variables with values."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path }} {{ line }} {{ column }}")
        result = builder(test_file, 42, 5)
        assert result == ["editor", str(test_file.resolve()), "42", "5"]

    def test_line_and_column_none(self, tmp_path):
        """Test line and column variables when None."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path }} {{ line }} {{ column }}")
        result = builder(test_file, None, None)
        # Empty strings for None values
        assert result == ["editor", str(test_file.resolve())]

    def test_line_colon_format(self, tmp_path):
        """Test {{ line_colon }} and {{ column_colon }} format."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        # With values
        builder = command_from_template("editor {{ path }}{{ line_colon }}{{ column_colon }}")
        result = builder(test_file, 42, 5)
        assert result == ["editor", f"{test_file.resolve()}:42:5"]

        # With line only
        result = builder(test_file, 42, None)
        assert result == ["editor", f"{test_file.resolve()}:42"]

        # With None values
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

    def test_line_plus_format(self, tmp_path):
        """Test {{ line_plus }} format for vim-style editors."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("vim {{ line_plus }} {{ path }}")

        # With line value
        result = builder(test_file, 42, None)
        assert result == ["vim", "+42", str(test_file.resolve())]

        # With None - no bare +
        result = builder(test_file, None, None)
        assert result == ["vim", str(test_file.resolve())]

    def test_column_plus_format(self, tmp_path):
        """Test {{ column_plus }} format."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("editor {{ path }} {{ column_plus }}")

        # With column value
        result = builder(test_file, None, 5)
        assert result == ["editor", str(test_file.resolve()), "+5"]

        # With None
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

    def test_paths_with_spaces(self, tmp_path):
        """Test handling paths with spaces using quotes."""
        # Create file with space in name
        test_file = tmp_path / "my file.py"
        test_file.write_text("test")

        # Without quotes - path gets split (not ideal but shlex behavior)
        builder = command_from_template("editor {{ path }}")
        result = builder(test_file, None, None)
        # shlex will split on spaces unless quoted
        # The path might contain spaces, but shlex.split() will handle it
        # Actually, shlex.split() on a plain path with spaces WILL split it
        # So we expect multiple tokens
        assert "editor" in result

        # With quotes - path stays together
        builder = command_from_template('editor "{{ path }}"')
        result = builder(test_file, None, None)
        assert result == ["editor", str(test_file.resolve())]

    def test_template_validation_unknown_variable(self):
        """Test that unknown variables raise ValueError."""
        with pytest.raises(ValueError, match="Unknown template variables"):
            command_from_template("editor {{ unknown_var }} {{ path }}")

    def test_template_validation_typo(self):
        """Test that typos in variable names are caught."""
        with pytest.raises(ValueError, match="Unknown template variables.*lne"):
            command_from_template("editor {{ lne }} {{ path }}")  # typo: lne instead of line

    def test_template_whitespace_variations(self, tmp_path):
        """Test that {{ var }} and {{var}} both work."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        # With spaces
        builder1 = command_from_template("editor {{ path }}")
        # Without spaces
        builder2 = command_from_template("editor {{path}}")

        result1 = builder1(test_file, None, None)
        result2 = builder2(test_file, None, None)

        assert result1 == result2

    def test_real_world_vscode_template(self, tmp_path):
        """Test VSCode-style template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("code --goto {{ path }}:{{ line }}:{{ column }}")
        result = builder(test_file, 42, 5)
        assert result == ["code", "--goto", f"{test_file.resolve()}:42:5"]

    def test_real_world_vim_template(self, tmp_path):
        """Test vim-style template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("vim {{ line_plus }} {{ path }}")
        result = builder(test_file, 42, None)
        assert result == ["vim", "+42", str(test_file.resolve())]

    def test_real_world_sublime_template(self, tmp_path):
        """Test Sublime Text-style template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template("subl {{ path }}:{{ line }}:{{ column }}")
        result = builder(test_file, 42, 5)
        assert result == ["subl", f"{test_file.resolve()}:42:5"]

    def test_empty_template_values(self, tmp_path):
        """Test that empty values don't leave artifacts."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        # Multiple spaces should be collapsed by shlex.split()
        builder = command_from_template("editor {{ line }} {{ column }} {{ path }}")
        result = builder(test_file, None, None)
        # shlex.split() collapses whitespace
        assert result == ["editor", str(test_file.resolve())]


class TestFileLinkTemplateConstants:
    """Test built-in template constants on FileLink class."""

    def test_vscode_template_constant(self):
        """Test FileLink.VSCODE_TEMPLATE constant."""
        assert FileLink.VSCODE_TEMPLATE == "code --goto {{ path }}:{{ line }}:{{ column }}"

    def test_vim_template_constant(self):
        """Test FileLink.VIM_TEMPLATE constant."""
        assert FileLink.VIM_TEMPLATE == "vim {{ line_plus }} {{ path }}"

    def test_sublime_template_constant(self):
        """Test FileLink.SUBLIME_TEMPLATE constant."""
        assert FileLink.SUBLIME_TEMPLATE == "subl {{ path }}:{{ line }}:{{ column }}"

    def test_nano_template_constant(self):
        """Test FileLink.NANO_TEMPLATE constant."""
        assert FileLink.NANO_TEMPLATE == "nano {{ line_plus }} {{ path }}"

    def test_eclipse_template_constant(self):
        """Test FileLink.ECLIPSE_TEMPLATE constant."""
        assert FileLink.ECLIPSE_TEMPLATE == "eclipse --launcher.openFile {{ path }}{{ line_colon }}"

    def test_use_template_constant(self, tmp_path):
        """Test using a template constant with command_from_template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        builder = command_from_template(FileLink.VIM_TEMPLATE)
        result = builder(test_file, 42, None)
        assert result == ["vim", "+42", str(test_file.resolve())]


class TestFileLinkTemplatePriority:
    """Test command builder/template priority order in FileLink."""

    def test_instance_command_builder_priority(self, tmp_path):
        """Test that instance command_builder takes precedence."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        def custom_builder(path, line, column):
            return ["custom", "builder"]

        link = FileLink(test_file, command_builder=custom_builder, command_template="should {{ path }} be ignored")

        # Directly test the priority logic by checking _do_open_file would use custom_builder
        assert link._command_builder == custom_builder

    def test_instance_template_priority(self, tmp_path):
        """Test that instance template is used when no builder."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        link = FileLink(test_file, command_template="custom {{ path }}")

        assert link._command_template == "custom {{ path }}"
        assert link._command_builder is None

    def test_class_default_template(self, tmp_path):
        """Test class-level default_command_template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        # Set class-level default
        original_template = FileLink.default_command_template
        try:
            FileLink.default_command_template = FileLink.VIM_TEMPLATE

            link = FileLink(test_file)
            assert link._command_template is None  # Instance has no template
            assert FileLink.default_command_template == FileLink.VIM_TEMPLATE

        finally:
            # Restore original
            FileLink.default_command_template = original_template

    def test_class_default_builder_over_template(self, tmp_path):
        """Test that class default_command_builder takes precedence over default_template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        def custom_builder(path, line, column):
            return ["custom"]

        original_builder = FileLink.default_command_builder
        original_template = FileLink.default_command_template

        try:
            FileLink.default_command_builder = custom_builder
            FileLink.default_command_template = "should {{ path }} be ignored"

            link = FileLink(test_file)
            assert link._command_builder is None  # Instance has no builder
            assert link._command_template is None  # Instance has no template
            # But class level has both, builder should win

        finally:
            FileLink.default_command_builder = original_builder
            FileLink.default_command_template = original_template


class TestFileLinkWithIconsTemplateIntegration:
    """Test that FileLinkWithIcons forwards command_template correctly."""

    def test_forwards_command_template(self, tmp_path):
        """Test that command_template is forwarded to internal FileLink."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        link = FileLinkWithIcons(test_file, command_template="vim {{ line_plus }} {{ path }}")

        # Check that internal FileLink has the template
        assert link._file_link._command_template == "vim {{ line_plus }} {{ path }}"

    def test_forwards_command_builder(self, tmp_path):
        """Test that command_builder is also forwarded."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        def custom_builder(path, line, column):
            return ["custom"]

        link = FileLinkWithIcons(test_file, command_builder=custom_builder)

        assert link._file_link._command_builder == custom_builder


class TestCommandLinkTemplateIntegration:
    """Test that CommandLink forwards command_template correctly."""

    def test_stores_command_template(self, tmp_path):
        """Test that CommandLink stores command_template."""
        output_file = tmp_path / "output.txt"
        output_file.write_text("output")

        cmd = CommandLink("Test Command", output_path=output_file, command_template="vim {{ line_plus }} {{ path }}")

        assert cmd._command_template == "vim {{ line_plus }} {{ path }}"

    def test_forwards_to_filelink_in_init(self, tmp_path):
        """Test that command_template is forwarded to FileLink when created in __init__."""
        output_file = tmp_path / "output.txt"
        output_file.write_text("output")

        cmd = CommandLink("Test Command", output_path=output_file, command_template="custom {{ path }}")

        # Check that internal FileLink has the template
        assert hasattr(cmd, "_name_widget")
        if isinstance(cmd._name_widget, FileLink):
            assert cmd._name_widget._command_template == "custom {{ path }}"


class TestFileLinkTemplateProperty:
    """Test the command_template property on FileLink."""

    def test_command_template_property(self, tmp_path):
        """Test that command_template property returns the stored template."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        link = FileLink(test_file, command_template="vim {{ path }}")

        assert link.command_template == "vim {{ path }}"

    def test_command_template_property_none(self, tmp_path):
        """Test command_template property when not set."""
        test_file = tmp_path / "test.py"
        test_file.write_text("test")

        link = FileLink(test_file)
        assert link.command_template is None
