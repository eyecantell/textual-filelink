"""Test demo for custom keyboard shortcuts in FileLinkWithIcons."""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static, Footer

from textual_filelink import FileLinkWithIcons
from textual_filelink.icon import Icon


class CustomKeysTestApp(App):
    """Test app for custom keyboard shortcuts."""

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
        ("c", "clear_log", "Clear Log"),
    ]

    def __init__(self):
        super().__init__()
        self.event_count = 0
        self.event_log_widget = None

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("=== Custom Keyboard Shortcuts Test ===\n", classes="test-section")

            yield Static(
                "Test 1: Icon with key='s' (settings)\n"
                "Press 's' to trigger icon\n"
                "Expected: Log should show 'settings' icon clicked",
                classes="test-section"
            )

            # Test 1: Single icon with custom key
            test_file = Path(__file__)
            icons_test1 = [
                Icon(name="settings", icon="⚙️", clickable=True, key="s", tooltip="Settings"),
            ]
            yield FileLinkWithIcons(
                test_file,
                display_name="Test 1: key='s'",
                icons_after=icons_test1,
                id="test1",
            )

            yield Static(
                "\nTest 2: Multiple icons with different keys\n"
                "Press '1' for first icon, '2' for second, '3' for third\n"
                "Expected: Log shows which icon was clicked",
                classes="test-section"
            )

            # Test 2: Multiple icons with numeric keys
            icons_test2 = [
                Icon(name="icon1", icon="1️⃣", clickable=True, key="1", tooltip="Icon 1"),
                Icon(name="icon2", icon="2️⃣", clickable=True, key="2", tooltip="Icon 2"),
                Icon(name="icon3", icon="3️⃣", clickable=True, key="3", tooltip="Icon 3"),
            ]
            yield FileLinkWithIcons(
                test_file,
                display_name="Test 2: keys='1','2','3'",
                icons_before=icons_test2,
                id="test2",
            )

            yield Static(
                "\nTest 3: Icons with letter keys\n"
                "Press 'a', 'b', 'c' for respective icons\n"
                "Expected: Log shows which icon was clicked",
                classes="test-section"
            )

            # Test 3: Icons with letter keys
            icons_test3 = [
                Icon(name="alpha", icon="🅰️", clickable=True, key="a", tooltip="Alpha"),
                Icon(name="beta", icon="🅱️", clickable=True, key="b", tooltip="Beta"),
                Icon(name="charlie", icon="©️", clickable=True, key="c", tooltip="Charlie"),
            ]
            yield FileLinkWithIcons(
                test_file,
                display_name="Test 3: keys='a','b','c'",
                icons_after=icons_test3,
                id="test3",
            )

            yield Static(
                "\nTest 4: Non-clickable icon with key (should do nothing)\n"
                "Press 'x' - should NOT trigger anything\n"
                "Expected: No log entry",
                classes="test-section"
            )

            # Test 4: Non-clickable icon with key
            icons_test4 = [
                Icon(name="non_clickable", icon="❌", clickable=False, key="x", tooltip="Not clickable"),
            ]
            yield FileLinkWithIcons(
                test_file,
                display_name="Test 4: non-clickable key='x'",
                icons_before=icons_test4,
                id="test4",
            )

            # Event log
            self.event_log_widget = Static("=== Event Log (press 'c' to clear) ===\n", classes="event-log")
            yield self.event_log_widget

        yield Footer()

    def on_file_link_with_icons_icon_clicked(self, event: FileLinkWithIcons.IconClicked):
        """Handle icon clicked events."""
        self.event_count += 1

        # Get the path name as identifier
        path_name = event.path.name if event.path else "unknown"

        log_entry = f"[{self.event_count}] File={path_name}, Icon={event.icon_name}, Char={event.icon_char}"

        # Append to log (store in list and rebuild)
        if not hasattr(self, "_event_entries"):
            self._event_entries = []
        self._event_entries.append(log_entry)

        # Update display
        log_text = "=== Event Log (press 'c' to clear) ===\n" + "\n".join(self._event_entries)
        self.event_log_widget.update(log_text)

        # Also notify
        self.notify(f"Icon clicked: {event.icon_name}", title="Event", timeout=2)

    def action_clear_log(self):
        """Clear the event log."""
        self.event_count = 0
        self._event_entries = []
        self.event_log_widget.update("=== Event Log (press 'c' to clear) ===")
        self.notify("Log cleared", timeout=1)


if __name__ == "__main__":
    app = CustomKeysTestApp()
    app.run()
