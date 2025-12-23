"""Demo 2: FileLinkList - Add Selection Controls

This demo introduces FileLinkList, which provides uniform controls for file links:
- Toggle (checkbox) controls for selecting/deselecting files
- Remove (delete) buttons for removing files from the list
- Show/hide controls to customize the UI
- Event handling for toggle and remove actions
- Batch operations on selected items

This is useful for building file selection interfaces where users need to:
- Choose which files to work with
- Manage a list of files
- Provide feedback about selection state

We compare four different configurations side-by-side so you can see how
the show_toggles and show_remove parameters affect the UI.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import FileLink, FileLinkList


class FileLinkListBasicsApp(App):
    """Demonstrate different FileLinkList configurations."""

    TITLE = "Demo 2: FileLinkList - Selection Controls"
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

    FileLinkList {
        margin: 0 0 1 0;
        height: auto;
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI with four comparison columns."""
        yield Header()

        # Title
        yield Static("☑️ FileLinkList - Compare Configurations", id="title")

        # Four columns showing different configurations
        with Horizontal(id="columns"):
            # Column 1: Toggle only
            with Vertical(classes="column"):
                yield Static("Toggle Only", classes="column-title")
                yield Static("show_toggles=True, show_remove=False", classes="column-desc")
                yield FileLinkList(show_toggles=True, show_remove=False, id="list1")

            # Column 2: Remove only
            with Vertical(classes="column"):
                yield Static("Remove Only", classes="column-title")
                yield Static("show_toggles=False, show_remove=True", classes="column-desc")
                yield FileLinkList(show_toggles=False, show_remove=True, id="list2")

            # Column 3: Both controls
            with Vertical(classes="column"):
                yield Static("Both Controls", classes="column-title")
                yield Static("show_toggles=True, show_remove=True", classes="column-desc")
                yield FileLinkList(show_toggles=True, show_remove=True, id="list3")

            # Column 4: Batch operations
            with Vertical(classes="column"):
                yield Static("Batch Operations", classes="column-title")
                yield Static("Press 'a' to select all, 'd' to remove selected", classes="column-desc")
                yield FileLinkList(show_toggles=True, show_remove=True, id="list4")

        yield Footer()

    def on_mount(self) -> None:
        """Populate the lists after mounting."""
        # List 1: Toggle only
        list1 = self.query_one("#list1", FileLinkList)
        list1.add_item(FileLink(Path("sample_files/example.py"), id="list1-item1"))
        list1.add_item(FileLink(Path("sample_files/config.json"), id="list1-item2"))
        list1.add_item(FileLink(Path("sample_files/data.csv"), id="list1-item3"))

        # List 2: Remove only
        list2 = self.query_one("#list2", FileLinkList)
        list2.add_item(FileLink(Path("sample_files/notes.txt"), id="list2-item1"))
        list2.add_item(FileLink(Path("sample_files/Makefile"), id="list2-item2"))
        list2.add_item(FileLink(Path("sample_files/LICENSE"), id="list2-item3"))

        # List 3: Both controls
        list3 = self.query_one("#list3", FileLinkList)
        list3.add_item(FileLink(Path("sample_files/example.py"), id="list3-item1"), toggled=True)
        list3.add_item(FileLink(Path("sample_files/config.json"), id="list3-item2"))
        list3.add_item(FileLink(Path("sample_files/data.csv"), id="list3-item3"))

        # List 4: Batch operations
        list4 = self.query_one("#list4", FileLinkList)
        list4.add_item(FileLink(Path("sample_files/notes.txt"), id="list4-item1"), toggled=True)
        list4.add_item(FileLink(Path("sample_files/Makefile"), id="list4-item2"), toggled=True)
        list4.add_item(FileLink(Path("sample_files/LICENSE"), id="list4-item3"))

    def on_file_link_list_item_toggled(self, event: FileLinkList.ItemToggled) -> None:
        """Handle when a file's toggle state changes."""
        state = "✓ selected" if event.is_toggled else "○ deselected"
        self.notify(
            f"{event.item.path.name} {state}",
            title="Toggle",
            timeout=1.5,
        )

    def on_file_link_list_item_removed(self, event: FileLinkList.ItemRemoved) -> None:
        """Handle when an item is removed."""
        self.notify(
            f"🗑️ Removed: {event.item.path.name}",
            severity="warning",
            timeout=2,
        )

    def key_a(self) -> None:
        """Select all items in list 4."""
        list4 = self.query_one("#list4", FileLinkList)
        list4.toggle_all(True)
        self.notify("✓ Selected all files in list 4", timeout=1.5)

    def key_d(self) -> None:
        """Remove selected items from list 4."""
        list4 = self.query_one("#list4", FileLinkList)
        count = len(list4.get_toggled_items())
        list4.remove_selected()
        if count > 0:
            self.notify(f"🗑️ Removed {count} file(s) from list 4", severity="warning", timeout=2)


if __name__ == "__main__":
    app = FileLinkListBasicsApp()
    app.run()
