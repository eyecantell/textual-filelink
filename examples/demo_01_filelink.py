"""Demo 1: FileLink - Clickable File Links

This demo showcases FileLink, the foundation widget for opening files in editors.

Key Features Demonstrated:
- Basic clickable file links
- Line and column navigation
- Built-in editor support (VSCode, Vim, Nano, Eclipse)
- Custom editor configuration
- Keyboard shortcuts (enter/o to open files)
- Event handling

FileLink makes filenames clickable so users can open files directly from your TUI.
When clicked (or activated with enter/o), it opens the file in the configured editor.

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate between links
- Enter or O: Open the focused file
- Q: Quit
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import FileLink


def custom_sublime_command(path: Path, line: int | None, column: int | None) -> list[str]:
    """Custom command builder for Sublime Text.

    Sublime uses format: subl file.py:line:column
    This demonstrates how to create custom command builders for any editor.
    """
    location = f"{path}:{line or 1}:{column or 1}"
    return ["subl", location]


class FileLinkDemo(App):
    """Comprehensive FileLink demonstration."""

    TITLE = "Demo 1: FileLink - Clickable File Links"
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        layout: vertical;
    }

    #title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $boost;
    }

    #columns {
        width: 100%;
        height: auto;
        layout: horizontal;
        padding: 1;
    }

    .column {
        width: 1fr;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 0 1 0 0;
    }

    .column-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #editors {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 2 0 1 0;
    }

    .section-description {
        width: 100%;
        color: $text-muted;
        margin: 0 0 1 0;
    }

    FileLink {
        margin: 0 0 1 0;
    }

    .coord-label {
        width: auto;
        color: $text-muted;
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        yield Static("🔗 FileLink - Click Files to Open Them", id="title")

        # Section 1: Basic Usage with Line/Column Navigation
        with Horizontal(id="columns"):
            # Column 1: Simple file links
            with Vertical(classes="column"):
                yield Static("Basic File Links", classes="column-title")
                yield Static("Click to open at the beginning:")
                yield FileLink(Path("sample_files/README.md"), id="basic-readme")
                yield FileLink(Path("sample_files/example.py"), id="basic-example")
                yield FileLink(Path("sample_files/config.json"), id="basic-config")

            # Column 2: With line numbers
            with Vertical(classes="column"):
                yield Static("Line Navigation", classes="column-title")
                yield Static("Jump to a specific line:")
                with Horizontal():
                    yield FileLink(Path("sample_files/example.py"), line=10, id="line-example")
                    yield Static(":10", classes="coord-label")
                with Horizontal():
                    yield FileLink(Path("sample_files/Makefile"), line=1, id="line-makefile")
                    yield Static(":1", classes="coord-label")
                with Horizontal():
                    yield FileLink(Path("sample_files/data.csv"), line=5, id="line-data")
                    yield Static(":5", classes="coord-label")

            # Column 3: With line and column
            with Vertical(classes="column"):
                yield Static("Line & Column", classes="column-title")
                yield Static("Precise cursor positioning:")
                with Horizontal():
                    yield FileLink(Path("sample_files/example.py"), line=14, column=4, id="col-example")
                    yield Static(":14:4", classes="coord-label")
                with Horizontal():
                    yield FileLink(Path("sample_files/config.json"), line=3, column=8, id="col-config")
                    yield Static(":3:8", classes="coord-label")
                with Horizontal():
                    yield FileLink(Path("sample_files/notes.txt"), line=2, column=1, id="col-notes")
                    yield Static(":2:1", classes="coord-label")

        # Section 2: Editor Configuration
        with ScrollableContainer(id="editors"):
            yield Static("Editor Configuration", classes="section-title")
            yield Static(
                "FileLink supports multiple editors. Each link below uses a different editor.",
                classes="section-description",
            )

            sample_file = Path("sample_files/example.py")

            # Built-in editors
            yield Static("Built-in Editors:", classes="section-title")

            yield FileLink(
                sample_file,
                display_name="📝 VSCode (default)",
                command_builder=FileLink.vscode_command,
                tooltip="Opens with: code --goto file.py:line:column",
                id="editor-vscode",
            )

            yield FileLink(
                sample_file,
                display_name="🖥️  Vim (terminal)",
                command_builder=FileLink.vim_command,
                tooltip="Opens with: vim +line file.py",
                id="editor-vim",
            )

            yield FileLink(
                sample_file,
                display_name="📄 Nano (beginner-friendly)",
                command_builder=FileLink.nano_command,
                tooltip="Opens with: nano +line file.py",
                id="editor-nano",
            )

            yield FileLink(
                sample_file,
                display_name="☕ Eclipse IDE",
                command_builder=FileLink.eclipse_command,
                tooltip="Opens with: eclipse file.py",
                id="editor-eclipse",
            )

            yield FileLink(
                sample_file,
                display_name="📋 Copy path to clipboard",
                command_builder=FileLink.copy_path_command,
                tooltip="Copies path instead of opening",
                id="editor-copy",
            )

            # Custom command builder example
            yield Static("Custom Command Builder:", classes="section-title")
            yield Static(
                "You can create custom command builders for any editor. "
                "Example: Sublime Text (subl file.py:line:column)",
                classes="section-description",
            )

            yield FileLink(
                sample_file,
                display_name="🎨 Sublime Text (custom)",
                command_builder=custom_sublime_command,
                tooltip="Opens with: subl file.py:line:column",
                id="editor-sublime",
            )

            # Global default configuration
            yield Static("Global Configuration:", classes="section-title")
            yield Static(
                "Set a default editor for all FileLinks:\n"
                "  FileLink.default_command_builder = FileLink.vim_command\n\n"
                "Or detect the user's preferred editor from $EDITOR environment variable.",
                classes="section-description",
            )

        yield Footer()

    def on_file_link_opened(self, event: FileLink.Opened) -> None:
        """Handle FileLink open events.

        Note: FileLink.Opened is the modern event name (v0.3.0+).
        FileLink.Clicked is a backwards-compatible alias.
        """
        # Build notification message showing where the file opens
        location = ""
        if event.line is not None:
            location = f" at line {event.line}"
            if event.column is not None:
                location += f", column {event.column}"

        self.notify(
            f"📂 Opening: {event.path.name}{location}",
            title="FileLink",
            timeout=2,
        )

    def on_mount(self) -> None:
        """Show helpful message on startup."""
        sample_dir = Path("./examples/sample_files")
        if not sample_dir.exists():
            # Try relative to script location
            sample_dir = Path(__file__).parent / "sample_files"
            if not sample_dir.exists():
                self.notify(
                    "⚠️  Sample files not found at ./examples/sample_files\n"
                    "File paths will be relative to current directory.",
                    severity="warning",
                    timeout=5,
                )


if __name__ == "__main__":
    app = FileLinkDemo()
    app.run()
