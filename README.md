# textual-filelink
[![CI](https://github.com/eyecantell/textual-filelink/actions/workflows/ci.yml/badge.svg)](https://github.com/eyecantell/textual-filelink/actions/runs/19725973735)
[![PyPI](https://img.shields.io/pypi/v/textual-filelink.svg)](https://pypi.org/project/textual-filelink/)
[![Python Versions](https://img.shields.io/pypi/pyversions/textual-filelink.svg)](https://pypi.org/project/textual-filelink/)
[![Downloads](https://pepy.tech/badge/textual-filelink)](https://pepy.tech/project/textual-filelink)
[![Coverage](https://codecov.io/gh/eyecantell/textual-filelink/branch/main/graph/badge.svg)](https://codecov.io/gh/eyecantell/textual-filelink)
[![License](https://img.shields.io/pypi/l/textual-filelink.svg)](https://github.com/eyecantell/textual-filelink/blob/main/LICENSE)

Clickable file links for [Textual](https://github.com/Textualize/textual) applications. Open files in your editor directly from your TUI.

## Features

- 🔗 **Clickable file links** that open in your preferred editor (VSCode, vim, nano, etc.)
- ☑️ **Toggle controls** for selecting/deselecting files
- ❌ **Remove buttons** for file management interfaces
- 🎨 **Multiple status icons** with unicode support for rich visual feedback
- 📍 **Icon positioning** - place icons before or after filenames
- 🔢 **Icon ordering** - control display order with explicit indices
- 👆 **Clickable icons** - make icons interactive with click events
- 👁️ **Dynamic visibility** - show/hide icons on the fly
- 🎯 **Jump to specific line and column** in your editor
- 🔧 **Customizable command builders** for any editor
- 🎭 **Flexible layouts** - show/hide controls as needed
- 💬 **Tooltips** for all interactive elements
- 🚀 **Command orchestration** with play/stop controls and animated spinners
- ⌨️ **Keyboard accessible** - fully tabbable and navigable without a mouse

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
        yield FileLink("README.md", line=10, column=5)
    
    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.notify(f"Opened {event.path.name} at line {event.line}")

if __name__ == "__main__":
    MyApp().run()
```

### ToggleableFileLink with Multiple Icons

```python
from textual_filelink import ToggleableFileLink

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield ToggleableFileLink(
            "script.py",
            initial_toggle=True,
            show_toggle=True,
            show_remove=True,
            icons=[
                {"name": "status", "icon": "✓", "clickable": True, "tooltip": "Validated"},
                {"name": "lock", "icon": "🔒", "position": "after", "tooltip": "Read-only"},
                {"name": "modified", "icon": "📝", "visible": False, "tooltip": "Modified"},
            ],
            toggle_tooltip="Toggle selection",
            remove_tooltip="Remove file",
            line=42
        )
    
    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.notify(f"{event.path.name} toggled: {event.is_toggled}")
    
    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.notify(f"{event.path.name} removed")
    
    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        self.notify(f"Clicked '{event.icon_name}' icon on {event.path.name}")
        
        # Example: dynamically update icon
        link = event.control
        link.update_icon("status", icon="⏳", tooltip="Processing...")

if __name__ == "__main__":
    MyApp().run()
```

### CommandLink for Command Orchestration


✅ ▶️ Build   ⚙️ ×   - last run successful, play button ot start again, command name ("Build"), settings icon, remove icon
❌ ▶️ Build   ⚙️ ×   - last run failed, play button to start again, command name ("Build"), settings icon, remove icon
⠧  ⏹️ Build   ⚙️ ×   - spinner, stop button to cancel run, command name ("Build"), settings icon, remove icon


```python
from textual_filelink import CommandLink

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield CommandLink(
            "Run Tests",
            initial_status_icon="❓",
            initial_status_tooltip="Not run yet",
        )

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(running=True, tooltip="Running...")
        # Start your command here

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(icon="⏹", running=False, tooltip="Stopped")

if __name__ == "__main__":
    MyApp().run()
```

## Keyboard Navigation

All FileLink widgets are fully keyboard accessible and can be navigated using the standard terminal keyboard shortcuts:

- **Tab** - Move focus to the next widget
- **Shift+Tab** - Move focus to the previous widget
- **Mouse Click** - Activate/interact with focused widgets

When a FileLink widget has focus, it displays a visual indicator (border with accent color). Future versions will add keyboard bindings (Enter, Space) for activating widgets without a mouse.

```python
class KeyboardAccessibleApp(App):
    def compose(self) -> ComposeResult:
        yield FileLink("file1.py", name="link1")
        yield FileLink("file2.py", name="link2")
        yield ToggleableFileLink("file3.py", name="link3")
        yield CommandLink("Run Tests", name="cmd1")

if __name__ == "__main__":
    # Now you can navigate with Tab and interact with arrow keys!
    KeyboardAccessibleApp().run()
```

**Focus Indicators:**
- Widgets display a border and background color when focused
- You can customize the focus appearance using CSS if desired

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
    icons: list[IconConfig | dict] | None = None,
    line: int | None = None,
    column: int | None = None,
    command_builder: Callable | None = None,
    disable_on_untoggle: bool = False,
    toggle_tooltip: str | None = None,
    remove_tooltip: str | None = None,
    name: str | None = None,
    id: str | None = None,
    classes: str | None = None,
)
```

**Parameters:**
- `path`: Full path to the file
- `initial_toggle`: Whether the item starts toggled (checked)
- `show_toggle`: Whether to display the toggle control (☐/☑)
- `show_remove`: Whether to display the remove button (×)
- `icons`: List of icon configurations (see IconConfig below)
- `line`: Optional line number to jump to
- `column`: Optional column number to jump to
- `command_builder`: Custom function to build the editor command
- `disable_on_untoggle`: If True, dim/disable the link when untoggled
- `toggle_tooltip`: Optional tooltip text for the toggle button
- `remove_tooltip`: Optional tooltip text for the remove button

### IconConfig

Icons can be specified as dicts or `IconConfig` dataclasses:

```python
from textual_filelink.toggleable_file_link import IconConfig

# As dict
{"name": "status", "icon": "✓", "clickable": True, "tooltip": "Done"}

# As dataclass
IconConfig(name="status", icon="✓", clickable=True, tooltip="Done")
```

**IconConfig Properties:**
- `name` (str, **required**): Unique identifier for the icon
- `icon` (str, **required**): Unicode character to display
- `position` (str): "before" or "after" the filename (default: "before")
- `index` (int | None): Explicit ordering index (default: None = use list order)
- `visible` (bool): Whether icon is initially visible (default: True)
- `clickable` (bool): Whether icon posts `IconClicked` messages (default: False)
- `tooltip` (str | None): Tooltip text (default: None)

### Properties

- `path: Path` - The file path
- `is_toggled: bool` - Current toggle state
- `icons: list[dict]` - List of all icon configurations
- `file_link: FileLink` - The internal FileLink widget

### Methods

#### `set_icon_visible(name: str, visible: bool)`
Show or hide a specific icon.

```python
link.set_icon_visible("warning", True)   # Show icon
link.set_icon_visible("warning", False)  # Hide icon
```

#### `update_icon(name: str, **kwargs)`
Update any properties of an existing icon.

```python
link.update_icon("status", icon="✓", tooltip="Complete")
link.update_icon("status", visible=False)
link.update_icon("status", position="after", index=5)
```

**Updatable properties:** `icon`, `position`, `index`, `visible`, `clickable`, `tooltip`

#### `get_icon(name: str) -> dict | None`
Get a copy of an icon's configuration.

```python
config = link.get_icon("status")
if config:
    print(f"Icon: {config['icon']}, Visible: {config['visible']}")
```

#### `set_toggle_tooltip(tooltip: str | None)`
Update the toggle button tooltip.

#### `set_remove_tooltip(tooltip: str | None)`
Update the remove button tooltip.

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

#### `ToggleableFileLink.IconClicked`
Posted when a clickable icon is clicked.

**Attributes:**
- `path: Path`
- `icon_name: str` - The name of the clicked icon
- `icon: str` - The unicode character of the icon

## CommandLink API

`CommandLink` is a specialized widget for command orchestration and status display, extending `ToggleableFileLink`. It's designed for single-instance commands (not multiple concurrent runs of the same command).

### Quick Start

```python
from textual_filelink import CommandLink

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield CommandLink(
            "Run Tests",
            output_path="test_output.log",
            initial_status_icon="❓",
            initial_status_tooltip="Not run yet",
            show_toggle=True,
            show_settings=True,
            show_remove=True,
        )

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        # Event provides full context: name, path, output_path, is_toggled
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(running=True, tooltip="Running tests...")
        self.run_worker(self.run_tests(link))

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        # Event provides full context including toggle state
        self.notify(f"Stopping {event.name}")

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        # Event provides full context for configuration
        self.notify(f"Settings for {event.name}")

    async def run_tests(self, link: CommandLink):
        # Simulate test run
        await asyncio.sleep(2)
        link.set_status(icon="✅", running=False, tooltip="All tests passed")
        link.set_output_path(Path("test_output.log"), tooltip="Click to view results")
```

### Constructor

```python
CommandLink(
    name: str,
    output_path: Path | str | None = None,
    *,
    initial_toggle: bool = False,
    initial_status_icon: str = "❓",
    initial_status_tooltip: str | None = None,
    running: bool = False,
    show_toggle: bool = True,
    show_settings: bool = True,
    show_remove: bool = True,
    toggle_tooltip: str | None = None,
    settings_tooltip: str | None = None,
    remove_tooltip: str | None = None,
    command_builder: Callable | None = None,
    disable_on_untoggle: bool = False,
)
```

**Parameters:**
- `name`: Command display name (also used as widget ID)
- `output_path`: Path to output file. If None, clicking command name does nothing
- `initial_toggle`: Whether the command starts toggled/selected
- `initial_status_icon`: Initial status icon (default: "❓")
- `initial_status_tooltip`: Initial tooltip for status icon
- `running`: Whether command is currently running. If True, shows spinner and stop button
- `show_toggle`: Whether to show the toggle checkbox
- `show_settings`: Whether to show the settings icon
- `show_remove`: Whether to show the remove button
- `toggle_tooltip`: Tooltip for toggle checkbox
- `settings_tooltip`: Tooltip for settings icon
- `remove_tooltip`: Tooltip for remove button
- `command_builder`: Custom command builder for opening output files
- `disable_on_untoggle`: If True, dim/disable when untoggled

### Layout

```
[toggle] [status/spinner] [play/stop] command_name [settings] [remove]
```

- **toggle**: Checkbox for selecting commands (inherited from ToggleableFileLink)
- **status/spinner**: Shows status icon, or animated spinner when running
- **play/stop**: ▶ when stopped, ⏹ when running
- **command_name**: Clickable link to output file (if set)
- **settings**: ⚙ icon for configuration
- **remove**: × button (inherited from ToggleableFileLink)

### Properties

- `name: str` - The command name (alias for display_name)
- `display_name: str` - The command display name (e.g., "Test", "Build")
- `output_path: Path | None` - Current output file path
- `path: Path | None` - The output file path (returns the actual output path, not a display path)
- `is_running: bool` - Whether the command is currently running
- `is_toggled: bool` - Current toggle state (inherited)

### Methods

#### `set_status(icon: str | None = None, tooltip: str | None = None, running: bool | None = None)`
Update command status display.

```python
# Start running (shows spinner)
link.set_status(running=True, tooltip="Running tests...")

# Complete with success
link.set_status(icon="✅", running=False, tooltip="All tests passed")

# Complete with failure
link.set_status(icon="❌", running=False, tooltip="3 tests failed")

# Update tooltip only
link.set_status(tooltip="Still running...")
```

#### `set_output_path(path: Path | str | None, tooltip: str | None = None)`
Update the output file path.

```python
link.set_output_path(Path("output.log"), tooltip="Click to view output")
link.set_output_path(None)  # Clear output path
```

#### `set_toggle(toggled: bool, tooltip: str | None = None)`
Update toggle state programmatically.

```python
link.set_toggle(True, tooltip="Selected for batch run")
link.set_toggle(False)
```

#### `set_settings_tooltip(tooltip: str | None)`
Update settings icon tooltip.

```python
link.set_settings_tooltip("Configure test options")
```

### Messages

#### `CommandLink.PlayClicked`
Posted when play button (▶) is clicked.

**Attributes:**
- `name: str` - The command name
- `path: Path | None` - The output file path (or None if not set)
- `output_path: Path | None` - The output file path (same as path)
- `is_toggled: bool` - Whether the command is selected for batch run

#### `CommandLink.StopClicked`
Posted when stop button (⏹) is clicked.

**Attributes:**
- `name: str` - The command name
- `path: Path | None` - The output file path (or None if not set)
- `output_path: Path | None` - The output file path (same as path)
- `is_toggled: bool` - Whether the command is selected for batch run

#### `CommandLink.SettingsClicked`
Posted when settings icon (⚙) is clicked.

**Attributes:**
- `name: str` - The command name
- `path: Path | None` - The output file path (or None if not set)
- `output_path: Path | None` - The output file path (same as path)
- `is_toggled: bool` - Whether the command is selected for batch run

**Inherited Messages:**
- `ToggleableFileLink.Toggled` - When toggle state changes
- `ToggleableFileLink.Removed` - When remove button is clicked

### Status Icons

Common status icons for commands:

```python
"❓"  # Not run / Unknown
"✅"  # Success / Passed
"❌"  # Failed / Error
"⚠️"  # Warning
"⏭️"  # Skipped
"🔄"  # Needs rerun
```

### Complete Example

```python
from pathlib import Path
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Static
from textual_filelink import CommandLink

class CommandRunnerApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Vertical {
        width: 60;
        height: auto;
        border: solid green;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("🚀 Command Runner")

            yield CommandLink(
                "Unit Tests",
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                settings_tooltip="Configure test options",
            )

            yield CommandLink(
                "Lint",
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                show_settings=False,
            )

            yield CommandLink(
                "Build",
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                settings_tooltip="Build configuration",
            )

        yield Footer()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(running=True, tooltip=f"Running {event.name}...")
        self.run_worker(self.simulate_command(link, event.name))

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(icon="⏹", running=False, tooltip="Stopped")
        self.notify(f"Stopped {event.name}", severity="warning")

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        self.notify(f"Settings for {event.name}")

    async def simulate_command(self, link: CommandLink, name: str):
        await asyncio.sleep(2)
        # Simulate success/failure
        import random
        if random.random() > 0.3:
            link.set_status(icon="✅", running=False, tooltip="Passed")
            link.set_output_path(Path(f"{name.lower().replace(' ', '_')}.log"))
            self.notify(f"{name} passed!", severity="information")
        else:
            link.set_status(icon="❌", running=False, tooltip="Failed")
            self.notify(f"{name} failed!", severity="error")

if __name__ == "__main__":
    CommandRunnerApp().run()
```

### Using Enriched Message Properties

As of version 0.2.0, CommandLink messages include enriched context that eliminates the need to query widgets in event handlers:

```python
class SmartCommandApp(App):
    def compose(self) -> ComposeResult:
        yield CommandLink("Tests", initial_status_icon="❓", show_toggle=True)
        yield CommandLink("Build", initial_status_icon="❓", initial_toggle=True)

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        """Event provides full context about the command."""
        # Instead of querying: link = self.query_one(f"#{event.name}", CommandLink)
        # Just use the event properties:

        self.log(f"Playing {event.name}")
        self.log(f"Output path: {event.path}")        # Path to output file
        self.log(f"Is toggled: {event.is_toggled}")   # Selected for batch run?

        # You still need to query for widget methods (like set_status),
        # but now you have context directly from the message
        link = self.query_one(f"#{event.name}", CommandLink)
        link.set_status(running=True, tooltip="Running...")

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        """Stop button includes state context."""
        # All message types (PlayClicked, StopClicked, SettingsClicked)
        # include: name, path, output_path, is_toggled
        self.notify(f"Stopping {event.name} (toggled={event.is_toggled})")

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        """Settings event has full context."""
        # Can now make decisions based on command state without querying
        if event.is_toggled:
            self.notify(f"Settings for {event.name} (part of batch run)")
        else:
            self.notify(f"Settings for {event.name} (standalone)")
```

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

## Icon Examples

### Icon Positioning

```python
# Icons before filename
ToggleableFileLink(
    path,
    icons=[
        {"name": "type", "icon": "🐍", "position": "before"},
        {"name": "status", "icon": "✓", "position": "before"},
    ]
)
# Display: 🐍 ✓ script.py

# Icons after filename
ToggleableFileLink(
    path,
    icons=[
        {"name": "size", "icon": "📊", "position": "after"},
        {"name": "sync", "icon": "☁️", "position": "after"},
    ]
)
# Display: script.py 📊 ☁️

# Mixed positions
ToggleableFileLink(
    path,
    icons=[
        {"name": "type", "icon": "🐍", "position": "before"},
        {"name": "sync", "icon": "☁️", "position": "after"},
    ]
)
# Display: 🐍 script.py ☁️
```

### Icon Ordering

```python
# Explicit ordering with index
ToggleableFileLink(
    path,
    icons=[
        {"name": "third", "icon": "3️⃣", "index": 3},
        {"name": "first", "icon": "1️⃣", "index": 1},
        {"name": "second", "icon": "2️⃣", "index": 2},
    ]
)
# Display: 1️⃣ 2️⃣ 3️⃣ filename.py

# Auto ordering (maintains list order)
ToggleableFileLink(
    path,
    icons=[
        {"name": "first", "icon": "A"},
        {"name": "second", "icon": "B"},
        {"name": "third", "icon": "C"},
    ]
)
# Display: A B C filename.py
```

### Dynamic Icon Updates

```python
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield ToggleableFileLink(
            "process.py",
            id="task-file",
            icons=[
                {"name": "status", "icon": "⏳", "tooltip": "Pending"},
                {"name": "result", "icon": "⚪", "visible": False},
            ]
        )
    
    def on_mount(self):
        # Simulate processing
        self.set_timer(2.0, self.complete_task)
    
    def complete_task(self):
        link = self.query_one("#task-file", ToggleableFileLink)
        link.update_icon("status", icon="✓", tooltip="Complete")
        link.set_icon_visible("result", True)
        link.update_icon("result", icon="🟢", tooltip="Success")
```

### Clickable Icons

```python
class MyApp(App):
    def compose(self) -> ComposeResult:
        yield ToggleableFileLink(
            path,
            icons=[
                {"name": "edit", "icon": "✏️", "clickable": True, "tooltip": "Edit settings"},
                {"name": "refresh", "icon": "🔄", "clickable": True, "tooltip": "Refresh"},
                {"name": "info", "icon": "ℹ️", "clickable": True, "tooltip": "Show info"},
            ]
        )
    
    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        if event.icon_name == "edit":
            self.edit_file(event.path)
        elif event.icon_name == "refresh":
            self.refresh_file(event.path)
        elif event.icon_name == "info":
            self.show_info(event.path)
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

### Plain Link with Icons
```python
ToggleableFileLink(
    path, 
    show_toggle=False, 
    show_remove=False,
    icons=[{"name": "type", "icon": "📄"}]
)
```
Display: `📄 filename.txt`

## Common Unicode Icons

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

# Actions
"✏️"  # Edit
"👁️"  # View
"🗑️"  # Delete
"💾"  # Save
"📋"  # Copy

# States
"🟢"  # Success/Green
"🟡"  # Warning/Yellow
"🔴"  # Error/Red
"⚪"  # Neutral/White
"🟣"  # Info/Purple
```

## Complete Example

```python
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical
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
                ]
            )
            
            # File needing review
            yield ToggleableFileLink(
                Path("config.json"),
                icons=[
                    {"name": "status", "icon": "⚠", "tooltip": "Needs review", "clickable": True},
                    {"name": "type", "icon": "⚙️", "tooltip": "Config file"},
                ]
            )
            
            # File being processed
            yield ToggleableFileLink(
                Path("data.csv"),
                id="processing-file",
                icons=[
                    {"name": "status", "icon": "⏳", "tooltip": "Processing...", "clickable": True},
                    {"name": "type", "icon": "📊", "tooltip": "Data file"},
                    {"name": "result", "icon": "⚪", "visible": False, "position": "after"},
                ]
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
- **Changelog**: https://github.com/eyecantell/textual-filelink/blob/main/CHANGELOG.md
- **Textual Documentation**: https://textual.textualize.io/