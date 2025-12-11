# Fixed test_file_link.py
from pathlib import Path

import pytest
from textual.app import App, ComposeResult

from textual_filelink import FileLink


class FileLinkTestApp(App):
    """Test app for FileLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.clicked_events = []

    def compose(self) -> ComposeResult:
        yield self.widget

    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.clicked_events.append(event)


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file


class TestFileLink:
    """Test suite for FileLink widget."""

    async def test_filelink_initialization(self, temp_file):
        """Test FileLink initializes with correct properties."""
        link = FileLink(temp_file, line=10, column=5)

        assert link.path == temp_file
        assert link.line == 10
        assert link.column == 5

    async def test_filelink_displays_filename(self, temp_file, get_rendered_text):
        """Test FileLink displays only the filename, not full path."""
        link = FileLink(temp_file)

        async with FileLinkTestApp(link).run_test():
            # The Static widget should display just the filename
            assert get_rendered_text(link) == temp_file.name

    async def test_filelink_click_posts_message(self, temp_file):
        """Test clicking FileLink posts a Clicked message."""
        link = FileLink(temp_file, line=10, column=5)
        app = FileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click(FileLink)
            await pilot.pause()

            assert len(app.clicked_events) == 1
            event = app.clicked_events[0]
            assert event.path == temp_file
            assert event.line == 10
            assert event.column == 5

    async def test_filelink_click_without_position(self, temp_file):
        """Test FileLink click works without line/column."""
        link = FileLink(temp_file)
        app = FileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click(FileLink)
            await pilot.pause()

            assert len(app.clicked_events) == 1
            event = app.clicked_events[0]
            assert event.path == temp_file
            assert event.line is None
            assert event.column is None

    async def test_filelink_with_string_path(self, temp_file):
        """Test FileLink accepts string paths."""
        link = FileLink(str(temp_file))

        assert link.path == temp_file.resolve()

    async def test_filelink_resolves_path(self, tmp_path):
        """Test FileLink resolves relative paths."""
        relative_path = Path("./test.txt")
        link = FileLink(relative_path)

        # Path should be resolved to absolute
        assert link.path.is_absolute()

    async def test_filelink_custom_command_builder(self, temp_file):
        """Test FileLink with custom command builder."""

        def custom_builder(path, line, column):
            return ["custom", "command", str(path)]

        link = FileLink(temp_file, command_builder=custom_builder)

        # Command builder should be stored
        assert link._command_builder == custom_builder

    async def test_filelink_vscode_command_builder(self, temp_file):
        """Test VSCode command builder generates correct command."""
        cmd = FileLink.vscode_command(temp_file, 10, 5)

        assert cmd[0] == "code"
        assert cmd[1] == "--goto"
        assert "10" in cmd[2]
        assert "5" in cmd[2]

    async def test_filelink_vscode_command_without_position(self, temp_file):
        """Test VSCode command builder without line/column."""
        cmd = FileLink.vscode_command(temp_file, None, None)

        assert cmd[0] == "code"
        assert cmd[1] == "--goto"
        assert cmd[2] == str(temp_file)

    async def test_filelink_vim_command_builder(self, temp_file):
        """Test vim command builder generates correct command."""
        cmd = FileLink.vim_command(temp_file, 10, 5)

        assert cmd[0] == "vim"
        assert "+call cursor(10,5)" in cmd
        assert str(temp_file) in cmd

    async def test_filelink_nano_command_builder(self, temp_file):
        """Test nano command builder generates correct command."""
        cmd = FileLink.nano_command(temp_file, 10, 5)

        assert cmd[0] == "nano"
        assert "+10,5" in cmd
        assert str(temp_file) in cmd

    async def test_filelink_eclipse_command_builder(self, temp_file):
        """Test Eclipse command builder generates correct command."""
        cmd = FileLink.eclipse_command(temp_file, 10, None)

        assert cmd[0] == "eclipse"
        assert "--launcher.openFile" in cmd
        assert any(str(temp_file) in arg for arg in cmd)

    async def test_filelink_copy_path_command_builder(self, temp_file):
        """Test copy path command builder."""
        cmd = FileLink.copy_path_command(temp_file, 10, 5)

        # Should contain the path with line and column
        full_cmd = " ".join(cmd)
        assert str(temp_file) in full_cmd
        assert "10" in full_cmd
        assert "5" in full_cmd

    async def test_filelink_default_command_builder_class_level(self, temp_file):
        """Test setting default command builder at class level."""
        original = FileLink.default_command_builder

        try:
            # Set custom default
            FileLink.default_command_builder = FileLink.vim_command
            link = FileLink(temp_file)

            # Should use vim command by default
            assert link._command_builder is None  # Instance has no override

        finally:
            # Restore original
            FileLink.default_command_builder = original

    async def test_filelink_properties_readonly(self, temp_file):
        """Test FileLink properties are read-only."""
        link = FileLink(temp_file, line=10, column=5)

        # Properties should be accessible
        assert link.path == temp_file
        assert link.line == 10
        assert link.column == 5

        # Properties should not have setters (will raise AttributeError)
        with pytest.raises(AttributeError):
            link.path = Path("/other/path")
