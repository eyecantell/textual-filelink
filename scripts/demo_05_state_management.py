"""Demo 5: State Management - Build Stateful File UIs

This demo teaches state management patterns for building stateful file UIs.

It demonstrates:
- Using dataclasses to track file state
- Multi-column layout with state synchronization
- Refreshing UI based on state changes
- Practical file workflow patterns
- Priority-based file management
- Batch operations based on state

Real-world use cases:
- File management applications
- Task/todo lists with categories
- Document workflows (draft → review → published)
- Download managers with status tracking

This is an intermediate demo. It's simpler than demo_file_link_improved.py
(3 columns vs 4) but teaches the same fundamental patterns.
"""

from dataclasses import dataclass
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import ToggleableFileLink


@dataclass
class FileState:
    """Track file state for UI management.

    This dataclass holds all the state for a single file, including:
    - Selection status (selected or not)
    - Archive status (archived or not)
    - Priority level (affects display icon)
    """

    name: str
    path: Path
    selected: bool = False
    archived: bool = False
    priority: str = "normal"  # "normal", "high", "urgent"

    def get_priority_icon(self) -> str:
        """Get icon based on priority level.

        Priority determines the visual indicator shown next to each file.
        This makes it easy to spot high-priority items at a glance.
        """
        return {
            "normal": "⚪",  # Gray circle
            "high": "🟡",   # Yellow circle
            "urgent": "🔴",  # Red circle
        }[self.priority]

    def get_priority_tooltip(self) -> str:
        """Get tooltip describing the priority level."""
        level_name = {
            "normal": "Normal priority",
            "high": "High priority",
            "urgent": "Urgent - needs attention!",
        }[self.priority]
        return f"Priority: {level_name} (click to change)"

    def cycle_priority(self) -> None:
        """Cycle priority to next level: normal → high → urgent → normal."""
        cycle = {"normal": "high", "high": "urgent", "urgent": "normal"}
        self.priority = cycle[self.priority]

    def get_all_files_link(self) -> ToggleableFileLink:
        """Create ToggleableFileLink for the All Files column.

        Shows all files with toggle control and priority indicator.
        """
        return ToggleableFileLink(
            self.path,
            initial_toggle=self.selected,
            show_toggle=True,
            show_remove=False,
            icons=[
                {
                    "name": "priority",
                    "icon": self.get_priority_icon(),
                    "tooltip": self.get_priority_tooltip(),
                    "clickable": False,  # Not clickable in this column
                }
            ],
        )

    def get_selected_link(self) -> ToggleableFileLink:
        """Create ToggleableFileLink for the Selected column.

        Shows selected files with toggle and remove controls.
        Priority icon is clickable here to change priorities.
        """
        return ToggleableFileLink(
            self.path,
            initial_toggle=True,
            show_toggle=True,
            show_remove=True,
            icons=[
                {
                    "name": "priority",
                    "icon": self.get_priority_icon(),
                    "tooltip": self.get_priority_tooltip(),
                    "clickable": True,  # Can click to change priority
                }
            ],
        )

    def get_archived_link(self) -> ToggleableFileLink:
        """Create ToggleableFileLink for the Archived column.

        Shows archived files in read-only mode with archive indicator.
        """
        return ToggleableFileLink(
            self.path,
            initial_toggle=False,
            show_toggle=False,
            show_remove=False,
            icons=[
                {
                    "name": "archived",
                    "icon": "📦",
                    "tooltip": "Archived file",
                }
            ],
        )


class ColumnContainer(Vertical):
    """A labeled column with a scrollable list of file links.

    This custom widget organizes a column header and scrollable content area.
    """

    DEFAULT_CSS = """
    ColumnContainer {
        width: 1fr;
        height: 100%;
        border: solid $primary;
    }

    ColumnContainer > Static {
        dock: top;
        width: 100%;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    ColumnContainer > ScrollableContainer {
        width: 100%;
        height: 1fr;
        padding: 1;
    }
    """

    def __init__(self, title: str, id: str | None = None):
        super().__init__(id=id)
        self.title = title
        self.container: ScrollableContainer | None = None

    def compose(self) -> ComposeResult:
        """Create the column header and scrollable container."""
        yield Static(self.title)
        self.container = ScrollableContainer()
        yield self.container

    def clear(self) -> None:
        """Remove all widgets from the scrollable container."""
        if self.container:
            for child in list(self.container.children):
                child.remove()


class StateManagementApp(App):
    """Demonstrate state management in file UIs."""

    TITLE = "Demo 5: State Management - Multi-Column File Organization"
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

    #main-container {
        width: 100%;
        height: 1fr;
        layout: horizontal;
    }

    .controls {
        width: 100%;
        height: auto;
        padding: 1;
        layout: horizontal;
    }

    Button {
        margin-right: 1;
    }
    """

    def __init__(self):
        super().__init__()
        # Central state: maps file path to its state
        self.file_states: dict[Path, FileState] = {}

        # Column containers
        self.all_files_column: ColumnContainer | None = None
        self.selected_column: ColumnContainer | None = None
        self.archived_column: ColumnContainer | None = None

    def compose(self) -> ComposeResult:
        """Create the UI with three-column layout."""
        yield Header()

        # Title
        yield Static(
            "📁 State Management - Select, Organize, and Archive Files",
            id="title",
        )

        # Three-column layout
        with Horizontal(id="main-container"):
            self.all_files_column = ColumnContainer("All Files", id="all-files")
            yield self.all_files_column

            self.selected_column = ColumnContainer("Selected", id="selected")
            yield self.selected_column

            self.archived_column = ColumnContainer("Archived", id="archived")
            yield self.archived_column

        # Control buttons
        with Horizontal(classes="controls"):
            yield Button("Select All", id="select-all", variant="primary")
            yield Button("Clear Selection", id="clear-selection")
            yield Button("Archive Selected", id="archive-selected", variant="warning")
            yield Button("Restore All", id="restore-all")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize state with sample files."""
        sample_dir = Path("./sample_files")

        if not sample_dir.exists():
            self.notify(
                "Warning: ./sample_files not found. Using current directory.",
                severity="warning",
                timeout=5,
            )
            sample_dir = Path(".")

        # Load all files from sample_files
        files = []
        if sample_dir.exists():
            for item in sample_dir.iterdir():
                if item.is_file():
                    files.append(item)

        # Sort alphabetically
        files.sort(key=lambda p: p.name.lower())

        # Create FileState for each file
        for file_path in files:
            resolved_path = file_path.resolve()
            self.file_states[resolved_path] = FileState(
                name=resolved_path.name,
                path=resolved_path,
            )

        # Populate columns
        self.refresh_all_columns()

        if not files:
            self.notify(
                "No files found in ./sample_files directory",
                severity="warning",
                timeout=5,
            )

    def refresh_all_columns(self) -> None:
        """Regenerate all columns from current state."""
        self.refresh_all_files_column()
        self.refresh_selected_column()
        self.refresh_archived_column()

    def refresh_all_files_column(self) -> None:
        """Regenerate the All Files column with all files."""
        if not self.all_files_column or not self.all_files_column.container:
            return

        self.all_files_column.clear()

        # Show all non-archived files, sorted
        for file_state in sorted(self.file_states.values(), key=lambda fs: fs.name.lower()):
            if not file_state.archived:
                link = file_state.get_all_files_link()
                self.all_files_column.container.mount(link)

    def refresh_selected_column(self) -> None:
        """Regenerate the Selected column with selected files."""
        if not self.selected_column or not self.selected_column.container:
            return

        self.selected_column.clear()

        # Show selected, non-archived files, sorted
        for file_state in sorted(self.file_states.values(), key=lambda fs: fs.name.lower()):
            if file_state.selected and not file_state.archived:
                link = file_state.get_selected_link()
                self.selected_column.container.mount(link)

    def refresh_archived_column(self) -> None:
        """Regenerate the Archived column with archived files."""
        if not self.archived_column or not self.archived_column.container:
            return

        self.archived_column.clear()

        # Show archived files, sorted
        for file_state in sorted(self.file_states.values(), key=lambda fs: fs.name.lower()):
            if file_state.archived:
                link = file_state.get_archived_link()
                self.archived_column.container.mount(link)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle control button presses."""
        if event.button.id == "select-all":
            # Select all non-archived files
            count = 0
            for file_state in self.file_states.values():
                if not file_state.archived:
                    file_state.selected = True
                    count += 1
            self.refresh_all_columns()
            self.notify(f"✓ Selected {count} files", timeout=1.5)

        elif event.button.id == "clear-selection":
            # Deselect all files
            count = 0
            for file_state in self.file_states.values():
                if file_state.selected:
                    file_state.selected = False
                    count += 1
            self.refresh_all_columns()
            self.notify(f"○ Deselected {count} files", timeout=1.5)

        elif event.button.id == "archive-selected":
            # Archive all selected files
            count = 0
            for file_state in self.file_states.values():
                if file_state.selected and not file_state.archived:
                    file_state.archived = True
                    file_state.selected = False
                    count += 1
            self.refresh_all_columns()
            self.notify(f"📦 Archived {count} files", timeout=1.5)

        elif event.button.id == "restore-all":
            # Restore all archived files
            count = 0
            for file_state in self.file_states.values():
                if file_state.archived:
                    file_state.archived = False
                    count += 1
            self.refresh_all_columns()
            self.notify(f"↩️ Restored {count} files", timeout=1.5)

    @on(ToggleableFileLink.Toggled)
    def handle_toggle(self, event: ToggleableFileLink.Toggled) -> None:
        """Handle toggle state changes in All Files column."""
        if event.path in self.file_states:
            file_state = self.file_states[event.path]
            file_state.selected = event.is_toggled
            self.refresh_all_columns()

            state = "✓ selected" if event.is_toggled else "○ deselected"
            self.notify(f"{event.path.name} {state}", timeout=1)

    @on(ToggleableFileLink.Removed)
    def handle_remove(self, event: ToggleableFileLink.Removed) -> None:
        """Handle remove button clicks in Selected column.

        Removing a file archives it (moves to Archived column).
        """
        if event.path in self.file_states:
            file_state = self.file_states[event.path]
            file_state.archived = True
            file_state.selected = False
            self.refresh_all_columns()

            self.notify(f"📦 {event.path.name} archived", timeout=1.5)

    @on(ToggleableFileLink.IconClicked)
    def handle_icon_click(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle priority icon clicks in Selected column.

        Clicking the priority icon cycles it to the next level.
        """
        if event.icon_name == "priority" and event.path in self.file_states:
            file_state = self.file_states[event.path]
            file_state.cycle_priority()

            # Refresh selected column to show updated icon
            self.refresh_selected_column()

            tooltip = file_state.get_priority_tooltip()
            self.notify(f"Priority changed: {tooltip}", timeout=1.5)


if __name__ == "__main__":
    app = StateManagementApp()
    app.run()
