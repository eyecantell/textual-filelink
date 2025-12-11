from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import ToggleableFileLink


class FileManagerApp(App):
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
    Static {
        width: 100%;
        content-align: center middle;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("📂 Project Files")

            # Validated file with multiple icons
            yield ToggleableFileLink(
                Path("main.py"),
                initial_toggle=True,
                icons=[
                    {"name": "status", "icon": "✓", "tooltip": "Validated", "clickable": True},
                    {"name": "type", "icon": "🐍", "tooltip": "Python file"},
                    {"name": "lock", "icon": "🔒", "position": "after", "tooltip": "Read-only"},
                ],
            )

            # File needing review
            yield ToggleableFileLink(
                Path("config.json"),
                icons=[
                    {"name": "status", "icon": "⚠", "tooltip": "Needs review", "clickable": True},
                    {"name": "type", "icon": "⚙️", "tooltip": "Config file"},
                ],
            )

            # File being processed
            yield ToggleableFileLink(
                Path("data.csv"),
                id="processing-file",
                icons=[
                    {"name": "status", "icon": "⏳", "tooltip": "Processing...", "clickable": True},
                    {"name": "type", "icon": "📊", "tooltip": "Data file"},
                    {"name": "result", "icon": "⚪", "visible": False, "position": "after"},
                ],
            )

        yield Footer()

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        state = "selected" if event.is_toggled else "deselected"
        self.notify(f"📋 {event.path.name} {state}")

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        # Remove the widget
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                child.remove()
        self.notify(f"🗑️ Removed {event.path.name}", severity="warning")

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        # Find the link by path
        link = None
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                link = child
                break

        if not link:
            return

        if event.icon_name == "status":
            # Toggle processing status
            if event.icon == "⏳":
                # Complete processing
                link.update_icon("status", icon="✓", tooltip="Complete")
                # Only update result icon if it exists (for data.csv)
                if link.get_icon("result"):
                    link.set_icon_visible("result", True)
                    link.update_icon("result", icon="🟢", tooltip="Success")
                self.notify(f"✅ {event.path.name} processing complete")
            else:
                # Start processing
                link.update_icon("status", icon="⏳", tooltip="Processing...")
                # Only hide result icon if it exists (for data.csv)
                if link.get_icon("result"):
                    link.set_icon_visible("result", False)
                self.notify(f"⏳ Processing {event.path.name}...")


if __name__ == "__main__":
    FileManagerApp().run()
