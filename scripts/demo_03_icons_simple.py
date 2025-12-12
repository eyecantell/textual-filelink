"""Demo 3: Icons - Add Visual Status and Metadata

This demo shows how to add multiple icons to file links for visual feedback.

Icons allow you to add status indicators, file type badges, and other visual
metadata to your file links. This demo demonstrates:
- Adding multiple icons per file
- Icon positioning (before or after the filename)
- Clickable icons that trigger events
- Updating icons dynamically
- Toggling icon visibility
- Using icons to show processing state

Real-world use cases:
- Status badges (✓ valid, ⚠️ warning, ✗ error)
- File type indicators (🐍 Python, 📊 CSV, ⚙️ Config)
- Lock/readonly indicators (🔒)
- Processing state (⏳ loading, ✓ done, ❌ failed)
- Action buttons (↑ upload, ↓ download, 🔄 sync)

This is a simple example with just 3 files. See demo_04_icons_advanced.py
for more complex icon demonstrations.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import ToggleableFileLink


class IconsSimpleApp(App):
    """Demonstrate simple icon usage in file links."""

    TITLE = "Demo 3: Icons - Simple Status and Type Indicators"
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        align: center middle;
    }

    Vertical {
        width: 80;
        height: auto;
        border: solid green;
        padding: 1;
    }

    Static.title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 1;
    }

    Static.description {
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
    }

    ToggleableFileLink {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI with example files and icons."""
        yield Header()

        with Vertical():
            # Title and explanation
            yield Static("🎨 Icons for Status and Metadata", classes="title")
            yield Static(
                "Click the status icons to toggle processing state. Try toggling and removing files.",
                classes="description",
            )

            # File 1: Validated file with status check, type, and lock icons
            # Icons appear: ✓ [filename] 🐍 🔒
            yield ToggleableFileLink(
                Path("sample_files/example.py"),
                initial_toggle=True,
                icons=[
                    {
                        "name": "status",
                        "icon": "✓",
                        "tooltip": "Validated ✓ Click to toggle",
                        "clickable": True,
                    },
                    {"name": "type", "icon": "🐍", "tooltip": "Python file"},
                    {
                        "name": "lock",
                        "icon": "🔒",
                        "position": "after",
                        "tooltip": "Read-only",
                    },
                ],
            )

            # File 2: File needing review with warning status
            # Icons appear: ⚠️ [filename] ⚙️
            yield ToggleableFileLink(
                Path("sample_files/config.json"),
                icons=[
                    {
                        "name": "status",
                        "icon": "⚠",
                        "tooltip": "Needs review ⚠️ Click to toggle",
                        "clickable": True,
                    },
                    {"name": "type", "icon": "⚙️", "tooltip": "Config file"},
                ],
            )

            # File 3: File with processing state that can change
            # Icons appear: ⏳ [filename] 📊 ⚪
            # Clicking the status icon toggles between processing and done states
            yield ToggleableFileLink(
                Path("sample_files/data.csv"),
                id="processing-file",
                icons=[
                    {
                        "name": "status",
                        "icon": "⏳",
                        "tooltip": "Processing... ⏳ Click to toggle",
                        "clickable": True,
                    },
                    {"name": "type", "icon": "📊", "tooltip": "CSV data file"},
                    {
                        "name": "result",
                        "icon": "⚪",
                        "visible": False,
                        "position": "after",
                        "tooltip": "Result indicator",
                    },
                ],
            )

        yield Footer()

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled) -> None:
        """Handle when toggle checkbox is clicked."""
        state = "✓ selected" if event.is_toggled else "○ deselected"
        self.notify(f"📋 {event.path.name} {state}", timeout=1.5)

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed) -> None:
        """Handle when remove button is clicked.

        This demo removes the widget from the UI when the remove button is
        clicked, demonstrating how to handle file removal.
        """
        # Find and remove the widget
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                child.remove()
                break

        self.notify(f"🗑️ Removed {event.path.name}", severity="warning", timeout=2)

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle when a clickable icon is clicked.

        In this demo, the status icons are clickable. Clicking them toggles
        the processing state, showing different icons based on the state.
        """
        # Find the file link that was clicked
        link = None
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                link = child
                break

        if not link:
            return

        # Handle status icon clicks
        if event.icon_name == "status":
            if event.icon == "⏳":
                # Currently processing - toggle to done
                link.update_icon("status", icon="✓", tooltip="Complete ✓ Click to toggle")
                # Show the result icon
                if link.get_icon("result"):
                    link.set_icon_visible("result", True)
                    link.update_icon("result", icon="🟢", tooltip="Success!")
                self.notify(f"✅ {event.path.name} processing complete", timeout=2)
            else:
                # Currently done - toggle to processing
                link.update_icon("status", icon="⏳", tooltip="Processing... ⏳ Click to toggle")
                # Hide the result icon
                if link.get_icon("result"):
                    link.set_icon_visible("result", False)
                self.notify(f"⏳ {event.path.name} processing started...", timeout=2)


if __name__ == "__main__":
    app = IconsSimpleApp()
    app.run()
