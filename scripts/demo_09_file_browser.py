"""Demo 9: Real File Browser - Directory Navigation with File Type Icons

This demo builds a file browser with directory navigation and file filtering.

Demonstrates:
- Single directory view with file listings
- File type detection and emoji icons (20+ types)
- Click to navigate into directories
- ".." entry for parent directory navigation
- File filtering by pattern (*.py, test_*.py)
- Selection with checkboxes
- Batch operations on selected files
- Metadata display (file type, path)

Real-world use cases:
- Custom file browsers for applications
- File pickers with previews
- Project explorers
- File management tools
- Content navigation systems

Key patterns:
- Path.iterdir() for directory listing
- Extension-based file type detection
- fnmatch for pattern matching
- State-driven UI refresh (dataclass state)
- Togglable file selection

Prerequisites:
- Understand demo_05 (state management)
- Understand demo_04 (icon system)
- Familiar with pathlib.Path

Notes:
- This demo uses sample_files as starting directory
- File type icons are extension-based (add more as needed)
- Current directory shown in header
- Filter pattern is case-insensitive
"""

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header, Input, Static

from textual_filelink import ToggleableFileLink


# File type to emoji icon mapping
FILE_TYPE_ICONS = {
    # Programming languages
    ".py": "🐍",
    ".js": "📜",
    ".ts": "📘",
    ".jsx": "⚛️",
    ".tsx": "⚛️",
    ".java": "☕",
    ".cpp": "©️",
    ".c": "©️",
    ".rs": "🦀",
    ".go": "🐹",
    ".rb": "💎",
    # Data formats
    ".json": "⚙️",
    ".yaml": "⚙️",
    ".yml": "⚙️",
    ".xml": "📋",
    ".csv": "📊",
    ".sql": "🗄️",
    # Documents
    ".txt": "📄",
    ".md": "📝",
    ".pdf": "📕",
    ".doc": "📘",
    ".docx": "📘",
    # Images
    ".png": "🖼️",
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".gif": "🖼️",
    ".svg": "🎨",
    # Archives
    ".zip": "📦",
    ".tar": "📦",
    ".gz": "📦",
    ".rar": "📦",
    # Other
    ".log": "📋",
    ".env": "🔐",
    ".sh": "⚙️",
    ".Makefile": "🔨",
}


@dataclass
class BrowserState:
    """Track browser state (current directory, selection, filter)."""

    current_dir: Path
    selected_files: set[Path] = field(default_factory=set)
    filter_pattern: str = ""


class FileBrowserApp(App):
    """Simple file browser with navigation and filtering."""

    TITLE = "Demo 9: Real File Browser - Navigate & Filter Files"
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

    #header-info {
        width: 100%;
        height: 2;
        padding: 0 1;
        background: $panel;
        content-align: left middle;
    }

    #filter-input {
        width: 40;
        margin: 0 1;
    }

    #file-list {
        width: 100%;
        height: 1fr;
        overflow: auto;
        padding: 0 1;
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

    .file-entry {
        margin: 0 0 1 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.state = BrowserState(current_dir=Path("./sample_files"))

    def compose(self) -> ComposeResult:
        """Create the file browser UI."""
        yield Header()

        yield Static("📁 File Browser - Navigate & Filter", id="title")

        # Header with current path
        yield Static(f"📍 {self.state.current_dir.absolute()}", id="header-info")

        # Filter input
        yield Input(
            placeholder="Filter: *.py, test_*.py (leave empty for all)",
            id="filter-input",
        )

        # File list area
        yield Static(id="file-list")

        # Control buttons
        with Horizontal(classes="controls"):
            yield Button("Select All", id="select-all", variant="primary")
            yield Button("Clear Selection", id="clear-selection")
            yield Button("Open Selected", id="open-selected", variant="success")
            yield Button("Back", id="back-button")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize on mount."""
        self.load_directory()

    def load_directory(self, path: Path | None = None) -> None:
        """Load and display files in directory."""
        if path:
            self.state.current_dir = path.resolve()

        # Update header
        header = self.query_one("#header-info", Static)
        header.update(f"📍 {self.state.current_dir.absolute()}")

        # Clear file list
        file_list = self.query_one("#file-list", Static)
        file_list.children = []  # Clear children
        file_list_container = self.query_one("#file-list")
        for child in list(file_list_container.children):
            child.remove()

        # Get files and directories
        try:
            items = list(self.state.current_dir.iterdir())
        except PermissionError:
            self.notify(
                f"Permission denied accessing {self.state.current_dir}",
                severity="error",
            )
            return

        # Sort: directories first, then files, both alphabetically
        dirs = sorted([p for p in items if p.is_dir()], key=lambda p: p.name.lower())
        files = sorted([p for p in items if p.is_file()], key=lambda p: p.name.lower())

        # Add parent directory link if not at root
        file_list_container = self.query_one("#file-list")
        if self.state.current_dir.parent != self.state.current_dir:
            parent_link = ToggleableFileLink(
                self.state.current_dir.parent,
                show_toggle=False,
                show_remove=False,
                icons=[
                    {
                        "name": "icon",
                        "icon": "📁",
                        "tooltip": "Parent directory",
                        "position": "before",
                    }
                ],
                classes="file-entry",
            )
            file_list_container.mount(parent_link)

        # Apply filter to files
        filtered_items = []

        # Add directories (never filtered)
        for dir_path in dirs:
            filtered_items.append((dir_path, "📁", True))  # is_dir

        # Add filtered files
        filter_pattern = self.state.filter_pattern or "*"
        for file_path in files:
            if fnmatch.fnmatch(file_path.name, filter_pattern):
                icon = self._get_file_icon(file_path)
                filtered_items.append((file_path, icon, False))  # not a dir

        # Create FileLink widgets
        for item_path, icon, is_dir in filtered_items:
            link = ToggleableFileLink(
                item_path,
                initial_toggle=item_path in self.state.selected_files,
                show_remove=False,
                icons=[
                    {
                        "name": "type",
                        "icon": icon,
                        "tooltip": "Directory" if is_dir else f"File ({item_path.suffix})",
                        "position": "before",
                    }
                ],
                classes="file-entry",
            )
            file_list_container.mount(link)

    def _get_file_icon(self, path: Path) -> str:
        """Get emoji icon for file type."""
        suffix = path.suffix.lower()
        return FILE_TYPE_ICONS.get(suffix, "📄")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input changes."""
        self.state.filter_pattern = event.value.lower()
        self.load_directory()

    @on(ToggleableFileLink.Toggled)
    def handle_toggle(self, event: ToggleableFileLink.Toggled) -> None:
        """Handle file selection toggle."""
        if event.is_toggled:
            self.state.selected_files.add(event.path)
        else:
            self.state.selected_files.discard(event.path)

        self.notify(
            f"{'✓' if event.is_toggled else '○'} {event.path.name}",
            timeout=0.5,
        )

    @on(ToggleableFileLink.FileClicked)
    def handle_file_click(self, event: ToggleableFileLink.FileClicked) -> None:
        """Handle file/directory click."""
        if event.path.is_dir():
            self.load_directory(event.path)
        else:
            self.notify(f"Would open {event.path.name} (click link again)", timeout=2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "select-all":
            self._select_all()
        elif event.button.id == "clear-selection":
            self._clear_selection()
        elif event.button.id == "open-selected":
            self._open_selected()
        elif event.button.id == "back-button":
            self._go_back()

    def _select_all(self) -> None:
        """Select all files in current directory."""
        file_list = self.query_one("#file-list")
        for link in file_list.query(ToggleableFileLink):
            if link.path.is_file():  # Only select files, not directories
                self.state.selected_files.add(link.path)
                link.set_toggle(True)

        count = len([p for p in self.state.selected_files if p.is_file()])
        self.notify(f"✓ Selected {count} files")

    def _clear_selection(self) -> None:
        """Clear all selections."""
        file_list = self.query_one("#file-list")
        for link in file_list.query(ToggleableFileLink):
            self.state.selected_files.discard(link.path)
            link.set_toggle(False)

        self.notify("○ Cleared all selections")

    def _open_selected(self) -> None:
        """Open all selected files."""
        if not self.state.selected_files:
            self.notify("⚠ No files selected", severity="warning")
            return

        count = len(self.state.selected_files)
        self.notify(f"Would open {count} file(s) (not implemented in demo)")

    def _go_back(self) -> None:
        """Go to parent directory."""
        if self.state.current_dir.parent != self.state.current_dir:
            self.load_directory(self.state.current_dir.parent)
        else:
            self.notify("Already at root directory", severity="warning")


if __name__ == "__main__":
    app = FileBrowserApp()
    app.run()
