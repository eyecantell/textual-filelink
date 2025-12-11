"""Demo 1: Basic FileLink - Learn the Fundamentals

This is the simplest FileLink example. It demonstrates:
- Creating clickable file links in a TUI
- Opening files in your default editor
- Navigating to specific lines and columns
- Handling FileLink.Clicked events
- Simple event notifications

FileLink is the foundation widget. It makes filenames clickable so users can
open files directly from your TUI application. When clicked, it opens the file
in the user's configured editor (VSCode, vim, nano, etc.).

This demo shows FileLink in its simplest form - just clickable links to files,
with no toggle checkboxes or status icons. Perfect for getting started!
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import FileLink


def file_link_with_coords(file_path: Path, line: int | None = None, column: int | None = None):
    """Yield FileLink with coordinate display.

    This is a generator function that yields widgets to be composed.
    Use with 'yield from' in the compose() method.
    """
    yield FileLink(file_path, line=line, column=column)

    # Show coordinates in muted text
    if line is not None or column is not None:
        coords = ""
        if line is not None:
            coords = f":{line}"
        if column is not None:
            coords += f":{column}"
        yield Static(coords, classes="coord-label")


class BasicFileLinkApp(App):
    """A simple app demonstrating basic FileLink functionality."""

    TITLE = "Demo 1: Basic FileLink"
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
        height: 1fr;
        layout: horizontal;
        padding: 1;
    }

    .column {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }

    .column-title {
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
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

        # Title section
        yield Static("🔗 FileLink Basics - Click Files to Open Them", id="title")

        # Main content with three columns
        with Horizontal(id="columns"):
            # Column 1: Files without navigation
            with Vertical(classes="column"):
                yield Static("No Navigation", classes="column-title")
                yield Static("Just open the file at the beginning:")
                yield FileLink(Path("sample_files/README.md"))
                yield FileLink(Path("sample_files/example.py"))
                yield FileLink(Path("sample_files/config.json"))

            # Column 2: Files with line numbers
            with Vertical(classes="column"):
                yield Static("With Line Numbers", classes="column-title")
                yield Static("Jump to a specific line:")
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/example.py"), line=10)
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/Makefile"), line=1)
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/data.csv"), line=2)

            # Column 3: Files with line and column
            with Vertical(classes="column"):
                yield Static("With Line & Column", classes="column-title")
                yield Static("Jump to specific line and column:")
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/example.py"), line=13, column=4)
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/config.json"), line=3, column=8)
                with Horizontal():
                    yield from file_link_with_coords(Path("sample_files/notes.txt"), line=5, column=1)

        yield Footer()

    def on_file_link_clicked(self, event: FileLink.Clicked) -> None:
        """Handle FileLink click events.

        When a FileLink is clicked, we show a notification with details
        about what was clicked and where.
        """
        # Build a message showing where the user clicked
        location = ""
        if event.line is not None:
            location = f" at line {event.line}"
            if event.column is not None:
                location += f", column {event.column}"

        self.notify(
            f"📂 Clicked: {event.path.name}{location}",
            title="FileLink",
            timeout=2,
        )


if __name__ == "__main__":
    app = BasicFileLinkApp()
    app.run()
