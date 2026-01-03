"""Demo 2: FileLinkWithIcons - Icons for Status and Metadata

This demo showcases FileLinkWithIcons, which combines FileLink with customizable icons.

Key Features Demonstrated:
- Icons before and after filenames
- Icon positioning and layout
- Clickable icons with events
- Keyboard shortcuts for icons
- Dynamic icon updates
- Icon visibility toggling
- Status indicators and file type badges
- Interactive icon controls

Icons add visual context to file links - status (✅/❌), file type (🐍/📊),
actions (🔄/⚙️), and more. They can be static or interactive.

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate between widgets
- Enter or O: Open the focused file link
- 1-3: Global shortcuts - activate keyboard test icons (work anywhere)
- a-c: Widget shortcuts - activate keyboard test icons (only when focused)
- Q: Quit
"""

from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import FileLinkWithIcons, Icon


class FileLinkWithIconsDemo(App):
    """Comprehensive FileLinkWithIcons demonstration."""

    TITLE = "Demo 2: FileLinkWithIcons - Icons for Status and Metadata"
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

    #content {
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

    FileLinkWithIcons {
        margin: 0 0 1 0;
    }

    #controls {
        width: 100%;
        height: auto;
        padding: 1;
        border: solid $primary;
        margin: 1 0;
    }

    #controls Button {
        margin: 0 1 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        yield Static("🎨 FileLinkWithIcons - Visual Status and Metadata", id="title")

        with ScrollableContainer(id="content"):
            # Section 1: Basic Icon Positioning
            yield Static("Section 1: Icon Positioning", classes="section-title")
            yield Static(
                "Icons can be placed before or after the filename. Order is preserved from the list.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                icons_before=[
                    Icon(name="type", icon="🐍", tooltip="Python file"),
                    Icon(name="status", icon="✅", tooltip="Validated"),
                ],
                tooltip="Icons before filename",
                id="pos-before",
            )

            yield FileLinkWithIcons(
                Path("sample_files/config.json"),
                icons_after=[
                    Icon(name="lock", icon="🔒", tooltip="Read-only"),
                    Icon(name="sync", icon="☁️", tooltip="Synced to cloud"),
                ],
                tooltip="Icons after filename",
                id="pos-after",
            )

            yield FileLinkWithIcons(
                Path("sample_files/data.csv"),
                icons_before=[
                    Icon(name="type", icon="📊", tooltip="CSV data"),
                ],
                icons_after=[
                    Icon(name="size", icon="💾", tooltip="Large file"),
                    Icon(name="modified", icon="📝", tooltip="Recently modified"),
                ],
                tooltip="Icons before and after",
                id="pos-both",
            )

            # Section 2: Clickable Icons
            yield Static("Section 2: Clickable Icons", classes="section-title")
            yield Static(
                "Icons with clickable=True emit IconClicked events when clicked or activated with keyboard. "
                "Use keyboard shortcuts (1-9) to click icons when widget is focused.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="Build Script",
                icons_before=[
                    Icon(name="status", icon="❓", tooltip="Status: Unknown", clickable=True),
                ],
                icons_after=[
                    Icon(name="run", icon="▶️", tooltip="Run script", clickable=True),
                    Icon(name="settings", icon="⚙️", tooltip="Configure", clickable=True),
                ],
                id="build-script",
                tooltip="Click icons to trigger actions",
            )

            # Section 3: File Type Indicators
            yield Static("Section 3: File Type Indicators", classes="section-title")
            yield Static(
                "Use icons to show file types at a glance.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                icons_before=[Icon(name="type", icon="🐍", tooltip="Python")],
                id="type-python",
            )

            yield FileLinkWithIcons(
                Path("sample_files/config.json"),
                icons_before=[Icon(name="type", icon="⚙️", tooltip="Configuration")],
                id="type-config",
            )

            yield FileLinkWithIcons(
                Path("sample_files/data.csv"),
                icons_before=[Icon(name="type", icon="📊", tooltip="Data file")],
                id="type-data",
            )

            yield FileLinkWithIcons(
                Path("sample_files/README.md"),
                icons_before=[Icon(name="type", icon="📄", tooltip="Documentation")],
                id="type-doc",
            )

            yield FileLinkWithIcons(
                Path("sample_files/Makefile"),
                icons_before=[Icon(name="type", icon="🔨", tooltip="Build file")],
                id="type-build",
            )

            # Section 4: Status Indicators
            yield Static("Section 4: Status Indicators", classes="section-title")
            yield Static(
                "Show processing state, validation status, or errors.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="tests.py (passing)",
                icons_before=[Icon(name="status", icon="✅", tooltip="Tests passed")],
                id="test-passing",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="linter.py (warnings)",
                icons_before=[Icon(name="status", icon="⚠️", tooltip="3 warnings")],
                id="test-warning",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="build.py (failed)",
                icons_before=[Icon(name="status", icon="❌", tooltip="Build failed")],
                id="test-failed",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="deploy.py (running)",
                icons_before=[Icon(name="status", icon="⏳", tooltip="In progress...")],
                id="test-running",
            )

            # Section 5: Hidden Icons (Dynamic Visibility)
            yield Static("Section 5: Dynamic Icon Visibility", classes="section-title")
            yield Static(
                "Icons can be shown/hidden dynamically. Click buttons below to toggle icon visibility.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="Dynamic Icons Demo",
                icons_before=[
                    Icon(name="status", icon="✅", tooltip="Status (always visible)"),
                ],
                icons_after=[
                    Icon(name="warning", icon="⚠️", tooltip="Warning (toggle me)", visible=False),
                    Icon(name="error", icon="❌", tooltip="Error (toggle me)", visible=False),
                ],
                id="dynamic-icons",
            )

            with Horizontal(id="controls"):
                yield Button("Show Warning", id="show-warning", variant="primary")
                yield Button("Hide Warning", id="hide-warning")
                yield Button("Show Error", id="show-error", variant="primary")
                yield Button("Hide Error", id="hide-error")

            # Section 6: Keyboard Shortcuts (Global vs Widget-level)
            yield Static("Section 6: Keyboard Shortcuts - Global vs Widget-level", classes="section-title")
            yield Static(
                "This demonstrates TWO patterns:\n"
                "• Global shortcuts (1-3): Work ANYWHERE in the app, no focus needed\n"
                "• Widget shortcuts (a-c): Only work when widget is FOCUSED (Tab to focus)\n\n"
                "Try both: Press 1-3 from anywhere, then Tab here and press a-c.",
                classes="section-description",
            )

            yield FileLinkWithIcons(
                Path("sample_files/example.py"),
                display_name="Keyboard Test (Tab or click to focus, then try a-c)",
                icons_after=[
                    Icon(name="refresh", icon="🔄", tooltip="Refresh (global: 1, widget: a)", clickable=True, key="a"),
                    Icon(name="edit", icon="✏️", tooltip="Edit (global: 2, widget: b)", clickable=True, key="b"),
                    Icon(name="delete", icon="🗑️", tooltip="Delete (global: 3, widget: c)", clickable=True, key="c"),
                ],
                id="keyboard-test",
            )

        yield Footer()

    def on_file_link_with_icons_icon_clicked(self, event: FileLinkWithIcons.IconClicked) -> None:
        """Handle icon click events."""
        # Handle specific icons using the widget reference
        if event.icon_name == "status" and event.widget.id == "build-script":
            # Cycle through states: ❓ → ⏳ → ✅ → ❌ → ❓
            current_icon = event.icon_char
            if current_icon == "❓":
                event.widget.update_icon("status", icon="⏳", tooltip="Running...")
            elif current_icon == "⏳":
                event.widget.update_icon("status", icon="✅", tooltip="Success!")
            elif current_icon == "✅":
                event.widget.update_icon("status", icon="❌", tooltip="Failed!")
            elif current_icon == "❌":
                event.widget.update_icon("status", icon="❓", tooltip="Status: Unknown")

        # General notification
        self.notify(
            f"Icon clicked: {event.icon_name} ({event.icon_char}) on {event.path.name}",
            title="Icon Action",
            timeout=2,
        )

    def on_key(self, event: events.Key) -> None:
        """Handle global keyboard shortcuts for the keyboard test widget."""
        # Route number keys 1-3 to the keyboard test widget
        if event.key in ("1", "2", "3"):
            try:
                widget = self.query_one("#keyboard-test", FileLinkWithIcons)
                # Map keys to icon names
                icon_map = {
                    "1": "refresh",
                    "2": "edit",
                    "3": "delete",
                }
                icon_name = icon_map[event.key]

                # Find the icon to get its character
                for icon in widget._icons_after:
                    if icon.name == icon_name:
                        # Post the IconClicked message directly
                        widget.post_message(FileLinkWithIcons.IconClicked(widget, widget._path, icon.name, icon.icon))
                        event.prevent_default()
                        break
            except Exception:
                # Widget not found or error, ignore
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks for dynamic icon visibility."""
        dynamic_widget = self.query_one("#dynamic-icons", FileLinkWithIcons)

        if event.button.id == "show-warning":
            dynamic_widget.set_icon_visible("warning", True)
            self.notify("⚠️ Warning icon shown", timeout=1)
        elif event.button.id == "hide-warning":
            dynamic_widget.set_icon_visible("warning", False)
            self.notify("Warning icon hidden", timeout=1)
        elif event.button.id == "show-error":
            dynamic_widget.set_icon_visible("error", True)
            self.notify("❌ Error icon shown", timeout=1)
        elif event.button.id == "hide-error":
            dynamic_widget.set_icon_visible("error", False)
            self.notify("Error icon hidden", timeout=1)


if __name__ == "__main__":
    app = FileLinkWithIconsDemo()
    app.run()
