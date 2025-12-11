"""
Example app demonstrating multi-icon ToggleableFileLink functionality.

This shows:
- Multiple icons per file
- Icons before and after filename
- Clickable icons with event handling
- Dynamic icon updates
- Icon ordering with explicit indices
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import ToggleableFileLink


class MultiIconExampleApp(App):
    """Example app showing multi-icon ToggleableFileLink features."""

    CSS = """
    Screen {
        align: center middle;
    }

    Vertical {
        width: 100;
        height: auto;
        border: solid green;
        padding: 1;
    }

    .title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 1 0 0 0;
    }

    .controls {
        width: 100%;
        height: auto;
        margin: 1 0;
    }

    Button {
        margin: 0 1 0 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.file_paths = self._create_sample_files()
        self.processing_files = set()

    def _create_sample_files(self) -> list[Path]:
        """Create some sample file paths (don't need to exist for demo)."""
        return [
            Path("main.py"),
            Path("config.json"),
            Path("README.md"),
            Path("tests.py"),
            Path("docs.html"),
        ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("🎨 Multi-Icon ToggleableFileLink Demo", classes="title")

            # Section 1: Basic multi-icon usage
            yield Static("📝 Basic Multi-Icon Usage", classes="section-title")
            yield ToggleableFileLink(
                self.file_paths[0],
                initial_toggle=True,
                show_toggle=True,
                show_remove=True,
                icons=[
                    {"name": "status", "icon": "✓", "tooltip": "Validated", "clickable": True},
                    {"name": "modified", "icon": "📝", "tooltip": "Modified", "clickable": True},
                    {"name": "lock", "icon": "🔒", "tooltip": "Read-only", "position": "after"},
                ],
                toggle_tooltip="Toggle selection",
                remove_tooltip="Remove file",
            )

            # Section 2: Icons with different positions
            yield Static("⬅️➡️ Icons Before & After", classes="section-title")
            yield ToggleableFileLink(
                self.file_paths[1],
                icons=[
                    {"name": "type", "icon": "⚙️", "tooltip": "Config file", "position": "before"},
                    {"name": "status", "icon": "✓", "tooltip": "Valid", "position": "before"},
                    {"name": "size", "icon": "📊", "tooltip": "2.3 KB", "position": "after"},
                    {"name": "sync", "icon": "☁️", "tooltip": "Synced", "position": "after"},
                ],
            )

            # Section 3: Ordered icons with explicit indices
            yield Static("🔢 Explicit Ordering (indices)", classes="section-title")
            yield ToggleableFileLink(
                self.file_paths[2],
                icons=[
                    {"name": "third", "icon": "3️⃣", "index": 3, "tooltip": "Index 3"},
                    {"name": "first", "icon": "1️⃣", "index": 1, "tooltip": "Index 1"},
                    {"name": "second", "icon": "2️⃣", "index": 2, "tooltip": "Index 2"},
                ],
            )

            # Section 4: Dynamic icon updates
            yield Static("🔄 Dynamic Updates (click icons)", classes="section-title")
            yield ToggleableFileLink(
                self.file_paths[3],
                id="dynamic-link",
                icons=[
                    {"name": "process", "icon": "⏳", "tooltip": "Click to process", "clickable": True},
                    {"name": "status", "icon": "⚪", "tooltip": "Status: Pending", "visible": True},
                ],
            )

            # Section 5: Hidden icons (can be shown dynamically)
            yield Static("👁️ Visibility Toggle", classes="section-title")
            yield ToggleableFileLink(
                self.file_paths[4],
                id="visibility-link",
                icons=[
                    {"name": "visible", "icon": "✓", "tooltip": "Always visible", "visible": True},
                    {"name": "hidden", "icon": "⚠", "tooltip": "Hidden warning", "visible": False},
                    {"name": "error", "icon": "✗", "tooltip": "Hidden error", "visible": False},
                ],
            )

            # Controls
            with Horizontal(classes="controls"):
                yield Button("Show Warning", id="show-warning")
                yield Button("Show Error", id="show-error")
                yield Button("Hide All", id="hide-all")
                yield Button("Reset", id="reset")

        yield Footer()

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        """Handle toggle events."""
        state = "selected" if event.is_toggled else "deselected"
        self.notify(f"📋 {event.path.name} {state}")

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        """Handle remove events."""
        self.notify(f"🗑️ Removed {event.path.name}", severity="warning")
        # Find and remove the widget
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                child.remove()

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        """Handle icon click events."""
        self.notify(f"🖱️ Clicked '{event.icon}' ({event.icon_name}) on {event.path.name}")

        # Special handling for dynamic link
        if event.path.name == "tests.py" and event.icon_name == "process":
            self._process_file(event.path)

    def _process_file(self, path: Path):
        """Simulate processing a file with dynamic icon updates."""
        link = self.query_one("#dynamic-link", ToggleableFileLink)

        if path in self.processing_files:
            self.notify("⚠ File is already processing!", severity="warning")
            return

        self.processing_files.add(path)

        # Update icons to show processing
        link.update_icon("process", icon="⏳", tooltip="Processing...")
        link.update_icon("status", icon="🟡", tooltip="Status: Processing")

        # Simulate async processing with a timer
        self.set_timer(2.0, lambda: self._complete_processing(path))

    def _complete_processing(self, path: Path):
        """Complete the processing simulation."""
        link = self.query_one("#dynamic-link", ToggleableFileLink)

        # Update icons to show completion
        link.update_icon("process", icon="✓", tooltip="Click to reprocess")
        link.update_icon("status", icon="🟢", tooltip="Status: Complete")

        self.processing_files.discard(path)
        self.notify(f"✅ Processing complete for {path.name}", severity="information")

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses for visibility controls."""
        link = self.query_one("#visibility-link", ToggleableFileLink)

        if event.button.id == "show-warning":
            link.set_icon_visible("hidden", True)
            link.update_icon("hidden", tooltip="Warning shown!")
            self.notify("⚠ Warning icon shown")

        elif event.button.id == "show-error":
            link.set_icon_visible("error", True)
            link.update_icon("error", tooltip="Error shown!")
            self.notify("✗ Error icon shown", severity="error")

        elif event.button.id == "hide-all":
            link.set_icon_visible("hidden", False)
            link.set_icon_visible("error", False)
            self.notify("👁️ Hidden icons concealed")

        elif event.button.id == "reset":
            # Reset visibility link to initial state
            link.set_icon_visible("visible", True)
            link.set_icon_visible("hidden", False)
            link.set_icon_visible("error", False)

            # Reset dynamic link
            dynamic_link = self.query_one("#dynamic-link", ToggleableFileLink)
            dynamic_link.update_icon("process", icon="⏳", tooltip="Click to process")
            dynamic_link.update_icon("status", icon="⚪", tooltip="Status: Pending")
            self.processing_files.clear()

            self.notify("🔄 Reset complete")


if __name__ == "__main__":
    app = MultiIconExampleApp()
    app.run()
