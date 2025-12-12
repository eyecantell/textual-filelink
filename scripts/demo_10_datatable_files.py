"""Demo 10: DataTable Integration - Files in Table Format

This demo shows how to display file information in a table with clickable rows.

Demonstrates:
- Textual DataTable widget usage
- File metadata in columns (icon, name, size, type, status)
- Click row to open file
- Status indicators (✅ Valid, ⚠️ Large, 🔒 Locked)
- Formatted file sizes (human-readable)
- File type detection

Real-world use cases:
- File managers with metadata view
- Upload/download managers
- Project file explorers
- Content management systems
- Log file browsers

Key patterns:
- DataTable with multiple columns
- Row click event handling
- Status determination logic
- File metadata formatting
- Icon based file type display

Prerequisites:
- Understand demo_01 (FileLink basics)
- Basic DataTable knowledge

Notes:
- DataTable cells are string-based (not widgets)
- Uses row key to map back to Path object
- Status shows file health/readiness
- Sizes are human-readable (1.2 KB, not 1254)
"""

import os
from dataclasses import dataclass
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static


@dataclass
class FileRow:
    """Represents one file in the table."""

    path: Path
    icon: str
    name: str
    size: str
    file_type: str
    status: str


class DataTableFileApp(App):
    """Display files in DataTable format."""

    TITLE = "Demo 10: DataTable Integration - Tabular File View"
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        layout: vertical;
    }

    #title {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-style: bold;
        background: $boost;
    }

    DataTable {
        width: 100%;
        height: 1fr;
    }

    #info {
        width: 100%;
        height: 2;
        padding: 0 1;
        background: $panel;
        content-align: left middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Create DataTable UI."""
        yield Header()

        yield Static("📊 DataTable File Browser - Click Row to Open", id="title")

        yield DataTable(id="files-table")

        yield Static("Click any row to open the file", id="info")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize table and load files."""
        table = self.query_one("#files-table", DataTable)

        # Define columns
        table.add_columns(
            "Icon",
            "Name",
            "Size",
            "Type",
            "Status",
        )

        # Load files from sample_files directory
        sample_dir = Path("./sample_files")
        if not sample_dir.exists():
            sample_dir = Path(".")
            self.notify(
                "sample_files not found, using current directory",
                severity="warning",
                timeout=3,
            )

        # Get all files
        try:
            files = sorted(
                [p for p in sample_dir.iterdir() if p.is_file()],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            self.notify("Permission denied accessing directory", severity="error")
            files = []

        # Add rows to table
        for file_path in files:
            row = self._create_file_row(file_path)

            # Add row with path as key (for retrieval on click)
            table.add_row(
                row.icon,
                row.name,
                row.size,
                row.file_type,
                row.status,
                key=str(file_path),  # Use path as key
            )

        self.notify(f"Loaded {len(files)} files", timeout=2)

    def _create_file_row(self, path: Path) -> FileRow:
        """Create a FileRow from a Path object."""
        icon = self._get_file_icon(path)
        name = path.name
        size = self._format_size(path)
        file_type = path.suffix if path.suffix else "file"
        status = self._get_file_status(path)

        return FileRow(
            path=path,
            icon=icon,
            name=name,
            size=size,
            file_type=file_type,
            status=status,
        )

    def _get_file_icon(self, path: Path) -> str:
        """Get emoji icon for file type."""
        icons = {
            ".py": "🐍",
            ".txt": "📄",
            ".md": "📝",
            ".json": "⚙️",
            ".csv": "📊",
            ".js": "📜",
            ".yaml": "⚙️",
            ".yml": "⚙️",
            ".sh": "⚙️",
            ".log": "📋",
        }
        suffix = path.suffix.lower()
        return icons.get(suffix, "📄")

    def _format_size(self, path: Path) -> str:
        """Format file size as human-readable string."""
        try:
            size_bytes = path.stat().st_size
        except OSError:
            return "? B"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024

        return f"{size_bytes:.1f} TB"

    def _get_file_status(self, path: Path) -> str:
        """Determine file status indicator."""
        # Check if readable
        if not os.access(path, os.R_OK):
            return "🔒 Locked"

        # Check size
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > 100:
                return "⚠️ Large"
        except OSError:
            return "❌ Error"

        # Check if symlink
        if path.is_symlink():
            try:
                path.resolve(strict=True)
                return "🔗 Link"
            except (FileNotFoundError, RuntimeError):
                return "🔗 Broken"

        return "✅ Valid"

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection - open file."""
        # Get file info from visible rows
        sample_dir = Path("./sample_files") if Path("./sample_files").exists() else Path(".")
        try:
            files = sorted(
                [p for p in sample_dir.iterdir() if p.is_file()],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            return

        # Row index maps to file in sorted list
        if event.cursor_row < len(files):
            file_path = files[event.cursor_row]
            self.notify(f"Would open: {file_path.name}", timeout=2)


if __name__ == "__main__":
    app = DataTableFileApp()
    app.run()
