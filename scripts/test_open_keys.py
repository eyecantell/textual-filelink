"""Test demo for custom open_keys in FileLink."""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Static

from textual_filelink import FileLink


class OpenKeysTestApp(App):
    """Test app for custom open_keys."""

    CSS = """
    Screen {
        background: $surface;
    }

    VerticalScroll {
        padding: 1 2;
    }

    .test-section {
        margin: 1 0;
        padding: 1;
        background: $panel;
        border: solid $primary;
    }

    .event-log {
        height: auto;
        padding: 1;
        margin-top: 1;
        background: $background;
        border: solid $accent;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.event_count = 0
        self._event_entries = []
        self.event_log_widget = None

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("=== Custom open_keys Test ===\n", classes="test-section")

            yield Static(
                "Test 1: Default FileLink (press 'o' to open)\nFocus and press 'o' - should log 'Opened' event",
                classes="test-section",
            )

            # Test 1: Default FileLink with 'o' key
            test_file = Path(__file__)
            yield FileLink(test_file, display_name="Test 1: default 'o' key", id="test1")

            yield Static(
                "\nTest 2: Custom open_keys=['f2', 'enter']\n"
                "Focus and press 'f2' or 'enter' - should log 'Opened' event",
                classes="test-section",
            )

            # Test 2: Custom open_keys
            yield FileLink(
                test_file,
                display_name="Test 2: custom keys=['f2', 'enter']",
                open_keys=["f2", "enter"],
                id="test2",
            )

            yield Static(
                "\nTest 3: Custom open_keys=['x', 'y', 'z']\n"
                "Focus and press 'x', 'y', or 'z' - should log 'Opened' event",
                classes="test-section",
            )

            # Test 3: Custom open_keys with multiple keys
            yield FileLink(
                test_file,
                display_name="Test 3: custom keys=['x', 'y', 'z']",
                open_keys=["x", "y", "z"],
                id="test3",
            )

            # Event log
            self.event_log_widget = Static("=== Event Log ===", classes="event-log")
            yield self.event_log_widget

        yield Footer()

    def on_file_link_opened(self, event: FileLink.Opened):
        """Handle file opened events."""
        self.event_count += 1
        log_entry = f"[{self.event_count}] Opened: {event.path.name}"
        self._event_entries.append(log_entry)
        log_text = "=== Event Log ===\n" + "\n".join(self._event_entries)
        self.event_log_widget.update(log_text)
        self.notify(f"File opened: {event.path.name}", title="Event", timeout=2)


if __name__ == "__main__":
    app = OpenKeysTestApp()
    app.run()
