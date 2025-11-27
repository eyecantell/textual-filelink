# textual-filelink

[![PyPI](https://img.shields.io/pypi/v/textual-filelink.svg)](https://pypi.org/project/textual-filelink/)
[![Python Versions](https://img.shields.io/pypi/pyversions/textual-filelink.svg)](https://pypi.org/project/textual-filelink/)

[![Downloads](https://pepy.tech/badge/textual-filelink)](https://pepy.tech/project/textual-filelink)
[![License](https://img.shields.io/pypi/l/textual-filelink.svg)](https://github.com/eyecantell/textual-filelink/blob/main/LICENSE)

Clickable file links for [Textual](https://github.com/Textualize/textual) applications. Open files in your editor directly from your TUI.

## Features

- 🔗 **Clickable file links** that open in your preferred editor (VSCode, vim, nano, etc.)
- ☑️ **Toggle controls** for selecting/deselecting files
- ❌ **Remove buttons** for file management interfaces
- 🎨 **Status icons** with unicode support for visual feedback
- 🎯 **Jump to specific line and column** in your editor
- 🔧 **Customizable command builders** for any editor
- 🎭 **Flexible layouts** - show/hide controls as needed

## Installation

```bash
pip install textual-filelink
```

Or with PDM:

```bash
pdm add textual-filelink
```

## Quick Start

### Basic FileLink

```python
from pathlib import Path
from textual.app import App, ComposeResult
from textual_filelink import FileLink

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield FileLink(Path("README.md"), line=10, column=5)
    
    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.notify(f"Opened {event.path.name} at line {event.line}")

if __name__ == "__main__":
    MyApp().run()
```

### ToggleableFileLink with Status Icons

```python
from textual_filelink import ToggleableFileLink

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield ToggleableFileLink(
            Path("script.py"),
            initial_toggle=True,
            show_toggle=True,
            show_remove=True,
            status_icon="✓",
            line=42
        )
    
    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.notify(f"{event.path.name} toggled: {event.is_toggled}")
    
    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.notify(f"{event.path.name} removed")
```

## FileLink API

### Constructor

```python
FileLink(
    path: Path | str,
    *,
    line: int | None = None,
    column: int | None = None,
    command_builder: Callable | None = None,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
)
```

**Parameters:**
- `path`: Full path to the file
- `line`: Optional line number to jump to
- `column`: Optional column number to jump to
- `command_builder`: Custom function to build the editor command

### Properties

- `path: Path` - The file path
- `line: int | None` - The line number
- `column: int | None` - The column number

### Messages

#### `FileLink.Clicked`
Posted when the link is clicked.

**Attributes:**
- `path: Path`
- `line: int | None`
- `column: int | None`

## ToggleableFileLink API

### Constructor

```python
ToggleableFileLink(
    path: Path | str,
    *,
    initial_toggle: bool = False,
    show_toggle: bool = True,
    show_remove: bool = True,
    status_icon: str | None = None,
    line: int | None = None,
    column: int | None = None,
    command_builder: Callable | None = None,
    disable_on_untoggle: bool = False,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
)
```

**Parameters:**
- `path`: Full path to the file
- `initial_toggle`: Whether the item starts toggled (checked)
- `show_toggle`: Whether to display the toggle control (☐/✓)
- `show_remove`: Whether to display the remove button (×)
- `status_icon`: Optional unicode icon to display before the filename
- `line`: Optional line number to jump to
- `column`: Optional column number to jump to
- `command_builder`: Custom function to build the editor command
- `disable_on_untoggle`: If True, dim/disable the link when untoggled

### Properties

- `path: Path` - The file path
- `is_toggled: bool` - Current toggle state
- `status_icon: str | None` - Current status icon

### Methods

#### `set_status_icon(icon: str | None)`
Update the status icon. Pass `None` to hide it.

```python
link.set_status_icon("⚠")  # Warning
link.set_status_icon("✓")  # Success
link.set_status_icon("⏳")  # In progress
link.set_status_icon(None) # Hide icon
```

### Messages

#### `ToggleableFileLink.Toggled`
Posted when the toggle state changes.

**Attributes:**
- `path: Path`
- `is_toggled: bool`

#### `ToggleableFileLink.Removed`
Posted when the remove button is clicked.

**Attributes:**
- `path: Path`

## Custom Editor Commands

### Using Built-in Command Builders

```python
from textual_filelink import FileLink

# Set default for all FileLink instances
FileLink.default_command_builder = FileLink.vim_command

# Or per instance
link = FileLink(path, command_builder=FileLink.nano_command)
```

**Available builders:**
- `FileLink.vscode_command` - VSCode (default)
- `FileLink.vim_command` - Vim
- `FileLink.nano_command` - Nano
- `FileLink.eclipse_command` - Eclipse
- `FileLink.copy_path_command` - Copy path to clipboard

### Custom Command Builder

```python
def my_editor_command(path: Path, line: int | None, column: int | None) -> list[str]:
    """Build command for my custom editor."""
    cmd = ["myeditor"]
    if line:
        cmd.extend(["--line", str(line)])
    if column:
        cmd.extend(["--column", str(column)])
    cmd.append(str(path))
    return cmd

link = FileLink(path, command_builder=my_editor_command)
```

## Layout Configurations

### Toggle Only
```python
ToggleableFileLink(path, show_toggle=True, show_remove=False)
```
Display: `☐ filename.txt`

### Remove Only
```python
ToggleableFileLink(path, show_toggle=False, show_remove=True)
```
Display: `filename.txt ×`

### Both Controls
```python
ToggleableFileLink(path, show_toggle=True, show_remove=True)
```
Display: `☐ filename.txt ×`

### Neither (Plain Link with Status)
```python
ToggleableFileLink(path, show_toggle=False, show_remove=False, status_icon="📄")
```
Display: `📄 filename.txt`

## Status Icons

Common unicode icons you can use:

```python
# Status indicators
"✓"  # Success/Complete
"⚠"  # Warning
"✗"  # Error/Failed
"⏳"  # In progress
"🔒"  # Locked
"📝"  # Modified
"➕"  # New/Added
"➖"  # Deleted
"🔄"  # Syncing

# File types
"📄"  # Document
"📁"  # Folder
"🐍"  # Python file
"📊"  # Data file
"⚙️"  # Config file
```

## Complete Example

```python
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Static
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
    
    def __init__(self):
        super().__init__()
        self.selected_files = set()
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical():
            yield Static("📁 Project Files")
            
            files = [
                ("main.py", "✓", True),
                ("config.json", "⚠", False),
                ("README.md", "📝", False),
                ("tests.py", "⏳", False),
            ]
            
            for filename, icon, toggled in files:
                yield ToggleableFileLink(
                    Path(filename),
                    initial_toggle=toggled,
                    show_toggle=True,
                    show_remove=True,
                    status_icon=icon,
                    line=1,
                )
        
        yield Footer()
    
    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        if event.is_toggled:
            self.selected_files.add(event.path)
            self.notify(f"✓ Selected {event.path.name}")
        else:
            self.selected_files.discard(event.path)
            self.notify(f"☐ Deselected {event.path.name}")
    
    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.selected_files.discard(event.path)
        # Find and remove the widget
        for child in self.query(ToggleableFileLink):
            if child.path == event.path:
                child.remove()
        self.notify(f"❌ Removed {event.path.name}", severity="warning")
    
    def on_file_link_clicked(self, event):
        self.notify(f"Opening {event.path.name}...")

if __name__ == "__main__":
    FileManagerApp().run()
```

## Development

```bash
# Clone the repository
git clone https://github.com/eyecantell/textual-filelink.git
cd textual-filelink

# Install with dev dependencies
pdm install -d

# Run tests
pdm run pytest

# Run tests with coverage
pdm run pytest --cov

# Lint
pdm run ruff check .

# Format
pdm run ruff format .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual) by Textualize
- Inspired by the need for better file navigation in terminal applications

## Links

- **PyPI**: https://pypi.org/project/textual-filelink/
- **GitHub**: https://github.com/eyecantell/textual-filelink
- **Issues**: https://github.com/eyecantell/textual-filelink/issues
- **Textual Documentation**: https://textual.textualize.io/