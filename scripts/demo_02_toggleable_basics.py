"""Demo 2: ToggleableFileLink - Add Selection Controls

This demo introduces ToggleableFileLink, which builds on FileLink by adding:
- Toggle (checkbox) controls for selecting/deselecting files
- Remove (delete) buttons for removing files from the list
- Show/hide controls to customize the UI
- Event handling for toggle and remove actions
- The disable_on_untoggle feature for graying out unselected items

This is useful for building file selection interfaces where users need to:
- Choose which files to work with
- Manage a list of files
- Provide feedback about selection state

We compare four different configurations side-by-side so you can see how
the show_toggle and show_remove parameters affect the UI.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import ToggleableFileLink


class ToggleableBasicsApp(App):
    """Demonstrate different ToggleableFileLink configurations."""

    TITLE = "Demo 2: ToggleableFileLink - Selection Controls"
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

    .column-desc {
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
        height: auto;
    }

    ToggleableFileLink {
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI with four comparison columns."""
        yield Header()

        # Title
        yield Static("☑️ ToggleableFileLink - Compare Configurations", id="title")

        # Four columns showing different configurations
        with Horizontal(id="columns"):
            # Column 1: Toggle only
            with Vertical(classes="column"):
                yield Static("Toggle Only", classes="column-title")
                yield Static("show_toggle=True, show_remove=False", classes="column-desc")
                yield ToggleableFileLink(
                    Path("sample_files/example.py"),
                    show_toggle=True,
                    show_remove=False,
                    toggle_tooltip="Select this file",
                )
                yield ToggleableFileLink(
                    Path("sample_files/config.json"),
                    show_toggle=True,
                    show_remove=False,
                )
                yield ToggleableFileLink(
                    Path("sample_files/data.csv"),
                    show_toggle=True,
                    show_remove=False,
                )

            # Column 2: Remove only
            with Vertical(classes="column"):
                yield Static("Remove Only", classes="column-title")
                yield Static("show_toggle=False, show_remove=True", classes="column-desc")
                yield ToggleableFileLink(
                    Path("sample_files/notes.txt"),
                    show_toggle=False,
                    show_remove=True,
                    remove_tooltip="Remove this file",
                )
                yield ToggleableFileLink(
                    Path("sample_files/Makefile"),
                    show_toggle=False,
                    show_remove=True,
                )
                yield ToggleableFileLink(
                    Path("sample_files/LICENSE"),
                    show_toggle=False,
                    show_remove=True,
                )

            # Column 3: Both controls
            with Vertical(classes="column"):
                yield Static("Both Controls", classes="column-title")
                yield Static("show_toggle=True, show_remove=True", classes="column-desc")
                yield ToggleableFileLink(
                    Path("sample_files/example.py"),
                    initial_toggle=True,
                    show_toggle=True,
                    show_remove=True,
                    toggle_tooltip="Select",
                    remove_tooltip="Delete",
                )
                yield ToggleableFileLink(
                    Path("sample_files/config.json"),
                    show_toggle=True,
                    show_remove=True,
                )
                yield ToggleableFileLink(
                    Path("sample_files/data.csv"),
                    show_toggle=True,
                    show_remove=True,
                )

            # Column 4: Disable on untoggle
            with Vertical(classes="column"):
                yield Static("Disable When Unselected", classes="column-title")
                yield Static("disable_on_untoggle=True", classes="column-desc")
                yield ToggleableFileLink(
                    Path("sample_files/notes.txt"),
                    initial_toggle=True,
                    show_toggle=True,
                    show_remove=False,
                    disable_on_untoggle=True,
                    toggle_tooltip="Unchecking grays this out",
                )
                yield ToggleableFileLink(
                    Path("sample_files/Makefile"),
                    initial_toggle=True,
                    show_toggle=True,
                    show_remove=False,
                    disable_on_untoggle=True,
                )
                yield ToggleableFileLink(
                    Path("sample_files/LICENSE"),
                    show_toggle=True,
                    show_remove=False,
                    disable_on_untoggle=True,
                )

        yield Footer()

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled) -> None:
        """Handle when a file's toggle state changes."""
        state = "✓ selected" if event.is_toggled else "○ deselected"
        self.notify(
            f"{event.path.name} {state}",
            title="Toggle",
            timeout=1.5,
        )

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed) -> None:
        """Handle when the remove button is clicked.

        Note: This demo doesn't actually remove widgets, just shows a notification.
        In a real app, you'd remove the widget or update your data model here.
        """
        self.notify(
            f"🗑️ Marked for removal: {event.path.name}",
            severity="warning",
            timeout=2,
        )


if __name__ == "__main__":
    app = ToggleableBasicsApp()
    app.run()
