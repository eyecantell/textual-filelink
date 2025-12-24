"""Demo 3: FileLinkList - Container with Batch Operations

This demo showcases FileLinkList, a container for managing file link widgets with
uniform toggle/remove controls and batch operations.

Key Features Demonstrated:
- Toggle checkboxes for selection
- Remove buttons for deletion
- Batch operations (toggle all, remove selected)
- ID validation (required, unique)
- Mixed widget types (FileLink, FileLinkWithIcons)
- Automatic scrolling
- Event handling (ItemToggled, ItemRemoved)

FileLinkList wraps any widget uniformly with optional toggle/remove controls,
enforces explicit IDs, and provides batch operation methods.

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate between widgets and controls
- Enter or O: Open the focused file link
- T: Toggle the focused item (when focus is on a file link)
- X: Remove the focused item (when focus is on a file link)
- Q: Quit
"""

from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Static

from textual_filelink import FileLink, FileLinkList, FileLinkWithIcons, Icon, sanitize_id


class FileLinkListDemo(App):
    """Comprehensive FileLinkList demonstration."""

    TITLE = "Demo 3: FileLinkList - Container with Batch Operations"
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

    #main {
        width: 100%;
        height: 1fr;
        layout: horizontal;
    }

    #left-panel {
        width: 60%;
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }

    #right-panel {
        width: 40%;
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 1 0 0 0;
    }

    .description {
        width: 100%;
        color: $text-muted;
        margin: 0 0 1 0;
    }

    FileLinkList {
        height: auto;
        max-height: 15;
        min-height: 5;
        margin: 0 0 2 0;
    }

    #controls {
        width: 100%;
        height: auto;
        layout: vertical;
        border: solid $primary;
        padding: 1;
    }

    #controls Button {
        width: 100%;
        margin: 0 0 1 0;
    }

    #stats {
        width: 100%;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }

    #stats Label {
        width: 100%;
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        yield Static("📋 FileLinkList - Batch Operations", id="title")

        with Horizontal(id="main"):
            # Left panel: File lists
            with Vertical(id="left-panel"):
                yield Static("Section 1: Basic File List with Toggles", classes="section-title")
                yield Static(
                    "Toggle checkboxes allow selection. Use controls on right to manipulate.",
                    classes="description",
                )

                # Create empty list (items added in on_mount)
                yield FileLinkList(show_toggles=True, id="basic-list")

                yield Static("Section 2: List with Toggle & Remove", classes="section-title")
                yield Static(
                    "Both toggles and remove buttons. Click ❌ to remove individual items.",
                    classes="description",
                )

                # Create empty list (items added in on_mount)
                yield FileLinkList(
                    show_toggles=True,
                    show_remove=True,
                    id="mixed-list",
                )

            # Right panel: Controls and stats
            with Vertical(id="right-panel"):
                yield Static("Batch Operations", classes="section-title")

                with Vertical(id="controls"):
                    yield Button("Toggle All ON", id="toggle-all-on", variant="primary")
                    yield Button("Toggle All OFF", id="toggle-all-off")
                    yield Button("Remove Selected", id="remove-selected", variant="error")
                    yield Button("Clear All", id="clear-all", variant="warning")
                    yield Button("Add Random File", id="add-file", variant="success")
                    yield Button("Reset Demo", id="reset", variant="default")

                with Vertical(id="stats"):
                    yield Static("Statistics", classes="section-title")
                    yield Label("Basic List: 0 items", id="stat-basic")
                    yield Label("Mixed List: 0 items", id="stat-mixed")
                    yield Label("Selected: 0 items", id="stat-selected")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize lists with items and update stats."""
        self.reset_lists()

    def reset_lists(self) -> None:
        """Reset both lists to initial state."""
        # Get list widgets
        basic_list = self.query_one("#basic-list", FileLinkList)
        mixed_list = self.query_one("#mixed-list", FileLinkList)

        # Clear existing items
        basic_list.clear_items()
        mixed_list.clear_items()

        # Populate basic list
        sample_dir = Path("sample_files")
        for file_path in [
            sample_dir / "README.md",
            sample_dir / "example.py",
            sample_dir / "config.json",
            sample_dir / "data.csv",
            sample_dir / "Makefile",
        ]:
            try:
                basic_list.add_item(FileLink(file_path, id=sanitize_id(str(file_path))))
            except Exception as e:
                self.notify(f"Error adding {file_path.name}: {e}", severity="error")

        # Populate mixed list
        try:
            mixed_list.add_item(
                FileLinkWithIcons(
                    sample_dir / "example.py",
                    icons_before=[Icon(name="type", icon="🐍", tooltip="Python")],
                    id="py-example",
                ),
                toggled=True,  # Initially selected
            )

            mixed_list.add_item(
                FileLinkWithIcons(
                    sample_dir / "config.json",
                    icons_before=[Icon(name="type", icon="⚙️", tooltip="Config")],
                    id="json-config",
                )
            )

            mixed_list.add_item(
                FileLinkWithIcons(
                    sample_dir / "data.csv",
                    icons_before=[Icon(name="type", icon="📊", tooltip="Data")],
                    id="csv-data",
                )
            )
        except Exception as e:
            self.notify(f"Error adding to mixed list: {e}", severity="error")

        # Update statistics
        self.update_stats()

    def update_stats(self) -> None:
        """Update statistics display."""
        basic_list = self.query_one("#basic-list", FileLinkList)
        mixed_list = self.query_one("#mixed-list", FileLinkList)

        basic_count = len(basic_list)
        mixed_count = len(mixed_list)
        selected_count = len(basic_list.get_toggled_items()) + len(mixed_list.get_toggled_items())

        self.query_one("#stat-basic", Label).update(f"Basic List: {basic_count} items")
        self.query_one("#stat-mixed", Label).update(f"Mixed List: {mixed_count} items")
        self.query_one("#stat-selected", Label).update(f"Selected: {selected_count} items")

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts for toggle and remove."""
        # Get the currently focused widget
        focused = self.focused

        # Check if focused widget is a FileLink or FileLinkWithIcons
        if isinstance(focused, (FileLink, FileLinkWithIcons)):
            basic_list = self.query_one("#basic-list", FileLinkList)
            mixed_list = self.query_one("#mixed-list", FileLinkList)

            # Find which list contains this item
            target_list = None
            for item in basic_list.get_items():
                if item == focused:
                    target_list = basic_list
                    break
            if not target_list:
                for item in mixed_list.get_items():
                    if item == focused:
                        target_list = mixed_list
                        break

            if target_list:
                # Handle 't' for toggle
                if event.key == "t" and target_list._show_toggles:
                    # Find the wrapper for this item
                    wrapper = target_list._wrappers.get(focused.id)
                    if wrapper:
                        new_state = not wrapper.is_toggled
                        wrapper.set_toggled(new_state)
                        target_list.post_message(FileLinkList.ItemToggled(focused, new_state))
                        self.notify(f"{'Selected' if new_state else 'Deselected'}: {focused._path.name}", timeout=1)
                        self.update_stats()
                        event.prevent_default()

                # Handle 'x' for remove
                elif event.key == "x" and target_list._show_remove:
                    target_list.remove_item(focused)
                    self.notify(f"Removed: {focused._path.name}", timeout=1)
                    event.prevent_default()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        basic_list = self.query_one("#basic-list", FileLinkList)
        mixed_list = self.query_one("#mixed-list", FileLinkList)

        if event.button.id == "toggle-all-on":
            basic_list.toggle_all(True)
            mixed_list.toggle_all(True)
            self.notify("✓ All items selected", timeout=1)
            self.update_stats()

        elif event.button.id == "toggle-all-off":
            basic_list.toggle_all(False)
            mixed_list.toggle_all(False)
            self.notify("All items deselected", timeout=1)
            self.update_stats()

        elif event.button.id == "remove-selected":
            # Get selected items before removal
            selected = basic_list.get_toggled_items() + mixed_list.get_toggled_items()
            if not selected:
                self.notify("⚠ No items selected", severity="warning", timeout=2)
                return

            # Remove selected items
            basic_list.remove_selected()
            mixed_list.remove_selected()

            self.notify(f"🗑️ Removed {len(selected)} items", timeout=2)
            self.update_stats()

        elif event.button.id == "clear-all":
            # Confirm before clearing
            basic_list.clear_items()
            mixed_list.clear_items()
            self.notify("🗑️ All items cleared", timeout=2)
            self.update_stats()

        elif event.button.id == "reset":
            self.reset_lists()
            self.notify("🔄 Demo reset to initial state", timeout=2)

        elif event.button.id == "add-file":
            # Add a new file to the mixed list
            import random

            files = ["notes.txt", "LICENSE", "Makefile"]
            icons = [
                Icon(name="type", icon="📄", tooltip="Text"),
                Icon(name="type", icon="📜", tooltip="License"),
                Icon(name="type", icon="🔨", tooltip="Build"),
            ]

            file_name = random.choice(files)
            icon = random.choice(icons)

            # Generate unique ID
            import time

            unique_id = sanitize_id(f"{file_name}-{int(time.time() * 1000)}")

            try:
                mixed_list.add_item(
                    FileLinkWithIcons(
                        Path("sample_files") / file_name,
                        icons_before=[icon],
                        id=unique_id,
                    )
                )
                self.notify(f"➕ Added {file_name}", timeout=1)
                self.update_stats()
            except ValueError as e:
                self.notify(f"❌ Error: {e}", severity="error", timeout=3)

    def on_file_link_list_item_toggled(self, event: FileLinkList.ItemToggled) -> None:
        """Handle item toggle events."""
        self.update_stats()

    def on_file_link_list_item_removed(self, event: FileLinkList.ItemRemoved) -> None:
        """Handle item removal events."""
        # Get the item's path if it has one
        item_name = "item"
        if hasattr(event.item, "_path"):
            item_name = event.item._path.name

        self.notify(f"🗑️ Removed: {item_name}", timeout=2)
        self.update_stats()


if __name__ == "__main__":
    app = FileLinkListDemo()
    app.run()
