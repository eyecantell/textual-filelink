# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**textual-filelink** is a Python library providing clickable file link widgets for [Textual](https://github.com/Textualize/textual) TUI applications. It enables opening files in editors directly from terminal UIs with support for line/column navigation, customizable icons, toggle controls, and command orchestration.

**Current Version**: 0.8.0

The library exports these main widget classes and utilities:
- **FileLink**: Basic clickable filename link
- **FileLinkWithIcons**: FileLink with customizable icons (composition-based)
- **CommandLink**: Specialized widget for command orchestration with status icons, play/stop controls, and optional timer display
- **FileLinkList**: Container for managing widgets with uniform toggle/remove controls
- **Icon**: Dataclass for type-safe icon configuration
- **sanitize_id()**: Utility function for converting strings to valid widget IDs
- **format_duration()**: Format elapsed time as human-readable duration (new in v0.8.0)
- **format_time_ago()**: Format elapsed time as time-ago string (new in v0.8.0)

## Common Development Commands

### Building and Testing
```bash
# Install development dependencies
pdm install -G test -G lint -G dev

# Run all tests with coverage report
pdm run pytest --cov=src/textual_filelink --cov-report=term-missing

# Run a single test file
pdm run pytest tests/test_file_link.py

# Run specific test by name
pdm run pytest tests/test_file_link.py::test_click_opens_file

# Run tests with verbose output
pdm run pytest -vv

# Run tests matching a pattern
pdm run pytest -k "toggleable" -v
```

### Code Quality
```bash
# Check code with ruff (linting + formatting)
pdm run ruff check .

# Format code
pdm run ruff format .

# Check specific file
pdm run ruff check src/textual_filelink/file_link.py
```

### Development Tools
```bash
# Run example applications (examples/ directory)
pdm run python examples/demo_01_filelink.py

# Run textual dev mode (hot-reload for demo development)
pdm run textual-dev run examples/demo_01_filelink.py

# Build distribution package
pdm build
```

### Screen Captures with textual-capture
The `textual-capture` tool enables automated TUI screenshot sequences - perfect for LLM-driven review, documentation, and testing.

```bash
# Validate config without running (recommended first step)
pdm run textual-capture config.toml --dry-run

# Run the capture sequence
pdm run textual-capture config.toml

# Verbosity options
pdm run textual-capture config.toml --verbose # Show all actions
pdm run textual-capture config.toml --quiet   # Errors only
```

**Basic TOML Configuration**:
```toml
# Required fields
app_module = "demo_commandlink"           # Python module name (without .py)
app_class = "CommandOrchestratorApp"      # App class to instantiate

# Output configuration
output_dir = "./screenshots"              # Where to save files (default: ".")
formats = ["svg", "txt"]                  # Formats to generate (default: both)
capture_prefix = "mysequence"             # Prefix for auto-sequenced captures (default: "capture")

# Tooltip capture (enabled by default)
capture_tooltips = true                   # Auto-capture tooltips with screenshots
widget_selector = "*"                     # CSS selector for widgets (default: all)
tooltip_include_empty = false             # Include widgets without tooltips

# Screen and timing
screen_width = 100                        # Terminal width (default: 80)
screen_height = 40                        # Terminal height (default: 40)
initial_delay = 1.0                       # Wait before first action (default: 1.0)

# Action steps - executed in order
[[step]]
type = "press"
keys = ["tab", "tab", "enter"]            # List syntax (preferred)
pause_between = 0.2                       # Seconds between keys (optional)

[[step]]
type = "delay"
seconds = 1.0                             # Wait for animations/async operations

[[step]]
type = "click"
label = "Run Selected"                    # Click button by label text

[[step]]
type = "capture"
output = "after_click"                    # Custom name (optional)
# Creates: after_click.svg, after_click.txt, after_click_tooltips.txt
```

**Available Step Types**:
- `capture`: Take screenshot (`.svg` + `.txt` + `_tooltips.txt`). Use `output` for custom name or omit for auto-sequence
- `press`: Simulate key presses. Use list syntax: `keys = ["tab", "ctrl+s"]` with optional `pause_between`
- `click`: Click button by label text (e.g., `label = "Submit"`)
- `delay`: Wait specified seconds (e.g., `seconds = 1.5`)

**LLM Review Workflows**:

*Basic UI Review*:
```toml
formats = ["txt"]                         # Text for AI analysis
capture_tooltips = true                   # Include tooltip data

[[step]]
type = "capture"
output = "initial_state"
```

*Tooltip Audit*:
```toml
formats = []                              # Skip visual rendering (faster)
capture_tooltips = true
tooltip_include_empty = true              # Show missing tooltips

[[step]]
type = "capture"
output = "tooltip_audit"
```

Check `tooltip_audit_tooltips.txt` for widgets with `(no tooltip)`.

**File Outputs**:
Each capture creates up to 3 files:
- `{output}.svg` - Visual screenshot (if `formats` includes "svg")
- `{output}.txt` - Text representation (if `formats` includes "txt")
- `{output}_tooltips.txt` - Widget tooltips (if `capture_tooltips = true`)

For LLM analysis, read the `.txt` and `_tooltips.txt` files - they contain structured text perfect for parsing!

## Architecture Overview (Current: v0.3.0)

### Core Widget Hierarchy
```
Current v0.3.0 Architecture:

Static (Textual)
  └─ FileLink (basic clickable file link)

Horizontal (Textual)
  └─ FileLinkWithIcons (FileLink + icons via composition)

Horizontal (Textual)
  └─ ToggleableFileLink (inheritance-based, WILL BE DEPRECATED in v0.4.0)
       └─ CommandLink (inherits from ToggleableFileLink)

VerticalScroll (Textual)
  └─ FileLinkList (container for uniform controls)
       Contains: FileLinkListItem wrappers
         └─ Any widget (FileLink, FileLinkWithIcons, CommandLink, etc.)

Note: See refactor-2025-12-22.md for planned v0.4.0 architecture changes.
```

### FileLink (src/textual_filelink/file_link.py)
- **Responsibility**: Render a clickable filename that opens a file in an editor
- **Key Features**:
  - Custom `display_name` parameter (defaults to filename)
  - Runtime keyboard bindings via `open_keys` parameter
  - Supports multiple editor command builders (VSCode, Vim, Nano, Eclipse)
  - **Command templates** for easy editor configuration (NEW in v0.9.0)
  - Shows notifications on success/failure
  - Default is VSCode with `code --goto file:line:column`
- **Messages**:
  - `FileLink.Opened` (path, line, column) - Primary message (v0.3.0+)
  - `FileLink.Clicked` - **DEPRECATED**: Backwards-compatible alias for `Opened` (emits DeprecationWarning, will be removed in v1.0)
- **Keyboard Shortcuts**: Customizable via `open_keys` parameter (default: `["enter", "o"]`)
- **Methods**:
  - `set_path(path, display_name=None, line=None, column=None)` - Update file path
    - **v0.8.0 breaking change**: Passing None for line/column now clears them (previously preserved existing values)
    - Use case: Change file path and reset cursor position to start

**Command Templates (NEW in v0.9.0)**:
- **Built-in Template Constants**:
  - `FileLink.VSCODE_TEMPLATE` = `"code --goto {{ path }}:{{ line }}:{{ column }}"`
  - `FileLink.VIM_TEMPLATE` = `"vim {{ line_plus }} {{ path }}"`
  - `FileLink.SUBLIME_TEMPLATE` = `"subl {{ path }}:{{ line }}:{{ column }}"`
  - `FileLink.NANO_TEMPLATE` = `"nano {{ line_plus }} {{ path }}"`
  - `FileLink.ECLIPSE_TEMPLATE` = `"eclipse --launcher.openFile {{ path }}{{ line_colon }}"`

- **Template Variables** (9 available):
  - `{{ path }}` - Full absolute path
  - `{{ path_relative }}` - Path relative to cwd (falls back to absolute)
  - `{{ path_name }}` - Just the filename
  - `{{ line }}` - Line number (empty string if None)
  - `{{ column }}` - Column number (empty string if None)
  - `{{ line_colon }}` - `:line` format (e.g., `:42`, empty if None)
  - `{{ column_colon }}` - `:column` format (e.g., `:5`, empty if None)
  - `{{ line_plus }}` - `+line` format (e.g., `+42`, empty if None) - for vim
  - `{{ column_plus }}` - `+column` format (e.g., `+5`, empty if None)

- **Usage Examples**:
  ```python
  # Method 1: Use built-in template constant
  link = FileLink("file.py", line=42, command_template=FileLink.VIM_TEMPLATE)

  # Method 2: Custom template string
  link = FileLink("file.py", line=42,
                  command_template='myeditor "{{ path }}" --line {{ line }}')

  # Method 3: Class-level default for all FileLinks
  FileLink.default_command_template = FileLink.VIM_TEMPLATE

  # Method 4: Convert template to builder explicitly
  builder = command_from_template(FileLink.SUBLIME_TEMPLATE)
  link = FileLink("file.py", command_builder=builder)
  ```

- **Priority Order** (when opening files):
  1. Instance `command_builder` (explicit callable, highest priority)
  2. Instance `command_template` (converted to builder at runtime)
  3. Class `default_command_builder`
  4. Class `default_command_template` (converted to builder at runtime)
  5. Built-in `vscode_command` (fallback)

- **Template Limitations**:
  - Templates work great for simple formats (VSCode, Sublime, simple vim)
  - For complex conditional logic (e.g., vim's `cursor()` call), use custom `command_builder` function
  - Paths with spaces require quotes in template: `'editor "{{ path }}"'`

### FileLinkWithIcons (src/textual_filelink/file_link_with_icons.py)
- **Responsibility**: Compose FileLink with custom icons via composition (not inheritance)
- **Key Concepts**:
  - Uses `Icon` dataclass for type-safe icon configuration
  - Icons positioned via `icons_before` and `icons_after` lists
  - Layout: `[icons_before...] FileLink [icons_after...]`
  - Dynamic keyboard shortcuts for clickable icons (1-9 keys)
  - Runtime bindings created in `on_mount()` using `self._bindings.bind()`
  - **Supports `command_template` parameter** - forwards to internal FileLink (NEW in v0.9.0)
- **Messages**:
  - `FileLinkWithIcons.IconClicked` (path, icon_name, icon_char)
  - Plus `FileLink.Opened` from embedded FileLink
- **Properties**: `file_link` property provides access to internal FileLink widget
- **Methods**:
  - `set_path(path, display_name=None, line=None, column=None)` - Update file path, delegates to internal FileLink
    - Setting line/column to None clears them (v0.8.0 behavior)

### ToggleableFileLink (src/textual_filelink/toggleable_file_link.py)
⚠️ **DEPRECATED in v0.4.0**: This widget will be removed. Use `FileLinkWithIcons` + `FileLinkList` instead.

- **Responsibility**: FileLink with checkboxes, custom icons, and removal capability (inheritance-based)
- **Status**: Legacy widget maintained for backwards compatibility
- **Migration Path**: Use `FileLinkList` for toggles/remove, `FileLinkWithIcons` for icons

### CommandLink (src/textual_filelink/command_link.py)
- **Responsibility**: Orchestrate command execution with status display and controls
- **Current Design (v0.8.0)**: Standalone widget extending `Horizontal`
- **Key Concepts**:
  - Layout: `[status/spinner] [timer?] [▶️/⏹️] command_name [⚙️?]`
  - Animated spinner using `set_interval()` when running
  - Optional timer display with `show_timer=True` (added in v0.7.0, redesigned in v0.8.0)
  - Auto-generates widget ID from command name via `sanitize_id()`
  - **Class-level BINDINGS** (added in v0.8.0): Default bindings for enter/o, space/p, s
  - Runtime keyboard bindings: `open_keys`, `play_stop_keys`, `settings_keys` can override defaults
  - Internal attribute naming: `_command_running` (not `_running` to avoid Textual's MessagePump conflict)
  - **Supports `command_template` parameter** for output file opening (NEW in v0.9.0)
- **API (v0.8.0)**:
  - Constructor parameter: `command_name: str` (first positional parameter)
  - Constructor parameter: `show_timer: bool = False` - Enable timer display
  - Constructor parameter: `timer_field_width: int = 12` - Timer column width
  - Constructor parameter: `start_time: float | None = None` - Unix timestamp when command started (new in v0.8.0)
  - Constructor parameter: `end_time: float | None = None` - Unix timestamp when command completed (new in v0.8.0)
  - Property: `widget.command_name` returns the command name
  - Method: `set_start_time(timestamp: float | None)` - Set command start timestamp (new in v0.8.0)
  - Method: `set_end_time(timestamp: float | None)` - Set command end timestamp (new in v0.8.0)
  - Method: `set_status(..., start_time=None, end_time=None)` - Accepts timestamp parameters (updated in v0.8.0)
  - **REMOVED in v0.8.0**: `set_timer_data(duration_str, time_ago_str)` method (breaking change)
  - Textual's `name` parameter: Now available for widget identification
  - **Important**: `widget.name` returns Textual's widget name (str | None), NOT the command name
- **Timer Display (v0.8.0 - BREAKING CHANGE)**:
  - Widget now accepts Unix timestamps (from `time.time()`) instead of pre-formatted strings
  - Computes and formats relative times internally using `utils.format_duration()` and `utils.format_time_ago()`
  - Shows elapsed duration when running: "500ms", "2.4s", "1m 30s", "2h 5m", "1d 3h", "2w 3d"
  - Shows time-ago when not running: "5s ago", "2m ago", "3h ago", "2d ago", "1w ago"
  - Updates automatically every 1 second when enabled (no external polling required)
  - Right-justified within fixed-width column for alignment
  - Timer interval started in `on_mount()`, stopped in `on_unmount()`
  - Optimized to avoid unnecessary refreshes (only updates when display string changes)
  - Self-contained: Widget owns all time computation and display logic
  - Migration: Replace `set_timer_data(duration_str="12m 34s")` with `set_start_time(time.time())`
- **Messages**:
  - `CommandLink.PlayClicked` (widget, name, output_path) - Note: message.name is command name
  - `CommandLink.StopClicked` (widget, name, output_path) - Note: message.name is command name
  - `CommandLink.SettingsClicked` (widget, name, output_path) - Note: message.name is command name
  - `CommandLink.OutputClicked` (output_path)

### FileLinkList (src/textual_filelink/file_link_list.py)
- **Responsibility**: Container for managing ANY Textual Widget with uniform toggle/remove controls
- **Widget-Agnostic**: Accepts any Widget subclass, not just FileLink-based widgets
  - FileLink, FileLinkWithIcons, CommandLink
  - Standard Textual widgets (Button, Label, Input, etc.)
  - Custom Widget subclasses
- **Only Requirement**: All widgets must have explicit IDs set
- **Key Concepts**:
  - Inherits from `VerticalScroll` for automatic scrolling
  - Wraps any widget uniformly: `[toggle?] widget [remove?]`
  - Enforces explicit IDs on all items (validates uniqueness)
  - Batch operations: `toggle_all()`, `remove_selected()`, `get_toggled_items()`
  - Internal `FileLinkListItem` wrapper widget
- **Messages**:
  - `FileLinkList.ItemToggled` (item, is_toggled)
  - `FileLinkList.ItemRemoved` (item)
- **Methods**:
  - `add_item(widget, toggled=False)` - Add item (raises ValueError if no ID or duplicate)
  - `remove_item(widget)` - Remove item
  - `clear_items()` - Remove all items
  - `toggle_all(value)` - Set all toggles to value
  - `remove_selected()` - Remove all toggled items
  - `get_toggled_items()` - Get list of toggled widgets
  - `get_items()` - Get all widgets
  - `__len__()`, `__iter__()` - Standard container protocols

#### Widget Agnosticism

FileLinkList is genuinely widget-agnostic - it can wrap ANY Textual Widget subclass:

```python
from textual.widgets import Button, Label
from textual_filelink import FileLinkList, FileLink, CommandLink

# Create list
widget_list = FileLinkList(show_toggles=True, show_remove=True)

# Add FileLink widgets
widget_list.add_item(FileLink("file.py", id="file1"))

# Add CommandLink widgets (non-FileLink!)
widget_list.add_item(CommandLink("Build", id="cmd1"))

# Add standard Textual widgets
widget_list.add_item(Button("Click", id="btn1"))
widget_list.add_item(Label("Status", id="lbl1"))

# Add custom widgets
widget_list.add_item(MyCustomWidget(id="custom1"))
```

**Key Points**:
- No FileLink-specific dependencies in implementation
- Wrapper (FileLinkListItem) only manages layout, not widget functionality
- Messages expose the wrapped widget for type-aware handling
- Proven to work: CommandLink usage in demo_05_dev_orchestration.py

### Icon Dataclass (src/textual_filelink/icon.py)
```python
@dataclass
class Icon:
    name: str              # Unique identifier
    icon: str              # Unicode character
    tooltip: str = ""      # Tooltip text (optional)
    clickable: bool = True # Whether icon can be clicked
    key: str | None = None # Keyboard shortcut (optional)
    visible: bool = True   # Whether icon is displayed
```

**Validation (v0.8.0)**:
- `name` and `icon` cannot be empty or whitespace-only
- Raises `ValueError` if validation fails: "Icon name/character cannot be empty or whitespace-only"

### Utility Functions (src/textual_filelink/utils.py)
- `sanitize_id(name: str) -> str` - Convert any string to valid widget ID
  - Lowercases, converts spaces/paths to hyphens, removes special chars
- `command_from_template(template: str) -> Callable` - Create command builder from template (NEW in v0.9.0)
  - Converts Jinja2-style template strings to command builder functions
  - Supports 9 template variables (see FileLink documentation)
  - Validates template at creation time (raises ValueError for unknown variables)
  - Returns builder function: `Callable[[Path, int | None, int | None], list[str]]`
  - Example: `builder = command_from_template("vim {{ line_plus }} {{ path }}")`
  - Templates parsed with simple string replacement + `shlex.split()` for argument tokenization
  - No external dependencies (no Jinja2 library required)
- `format_duration(secs: float) -> str` - Format elapsed time as duration (NEW in v0.8.0)
  - Milliseconds (< 1s): "500ms", "999ms"
  - Decimal seconds (1-60s): "1.0s", "2.4s", "59.9s"
  - Compound units (≥ 60s): "1m 30s", "2h 5m", "1d 3h", "2w 3d"
  - Negative values return empty string
  - Used internally by CommandLink timer display
- `format_time_ago(secs: float) -> str` - Format elapsed time as time-ago (NEW in v0.8.0)
  - Single-unit display: "5s ago", "2m ago", "3h ago", "2d ago", "1w ago"
  - Negative values return empty string
  - Used internally by CommandLink timer display

### Logging (src/textual_filelink/logging.py)

Optional logging for debugging. NullHandler by default (library best practice).

**Quick Setup:**
```python
from textual_filelink import setup_logging
setup_logging(level="DEBUG")  # Console output

# Or use standard Python logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

**API Functions:**
- `setup_logging(level="DEBUG", format_string=None)` - Enable console logging
- `disable_logging()` - Remove all handlers except NullHandler
- `get_logger()` - Get package logger (for internal use)

**What Gets Logged:**
- **DEBUG**: File opens, command execution, validation, widget lifecycle
- **INFO**: Successful file opens
- **ERROR**: Command failures, timeouts, validation errors

**Logging by Component:**

*FileLink (Priority 1: Command Execution)*
- DEBUG: File opening (`path`, `line`, `col`), command execution, path resolution
- INFO: Successful file opens
- ERROR: Command failures, timeouts, exceptions

*FileLinkWithIcons (Priority 2: Validation)*
- DEBUG: Icon validation
- ERROR: Duplicate names/keys, key conflicts

*FileLinkList (Priority 2: List Management)*
- DEBUG: Item add/remove, toggle operations
- ERROR: Missing IDs, duplicate IDs

*CommandLink (Priority 3: Lifecycle)*
- DEBUG: Widget mounting/unmounting, timer start, status changes

**Example Usage:**
```python
from textual_filelink import setup_logging, FileLink

# Enable DEBUG logging
setup_logging(level="DEBUG")

# Logs: "Opening file: path=test.py, line=10, col=5"
# Logs: "Executing: code --goto test.py:10:5"
# Logs: "Opened test.py"
link = FileLink("test.py", line=10, column=5)
link.open_file()
```

## Testing Structure

- **tests/conftest.py**: Shared fixtures for all tests
- **tests/test_file_link.py**: FileLink unit tests
- **tests/test_file_link_with_icons.py**: FileLinkWithIcons unit tests
- **tests/test_toggleable_file_link.py**: ToggleableFileLink unit tests (legacy)
- **tests/test_command_link.py**: CommandLink unit tests
- **tests/test_file_link_list.py**: FileLinkList unit tests
- **tests/test_tooltip_enhancement.py**: Tooltip keyboard shortcut enhancement tests
- **tests/test_utils.py**: Utility function tests (format_duration, format_time_ago, sanitize_id) (NEW in v0.8.0)
- **tests/test_logging.py**: Logging infrastructure tests (NEW in v0.9.0)
- **tests/test_integration.py**: Integration tests with mock Textual apps

**Key Testing Pattern**: Tests use `pilot` fixture to simulate user interactions (clicks) and verify message emission.

### Pytest Configuration
- Coverage minimum: 90% (enforced in CI)
- Async mode: auto
- Fixtures: asyncio fixtures with function-level scope
- Markers: `@pytest.mark.slow`, `@pytest.mark.integration` available

## Important Implementation Details

### Message Naming Convention
- **v0.3.0**: `FileLink.Opened` is the primary message, with `FileLink.Clicked` as a backwards-compatible alias
- **v0.8.0**: `FileLink.Clicked` now emits a `DeprecationWarning` when instantiated
- **v1.0**: `FileLink.Clicked` will be removed (use `Opened` for all new code)

### Keyboard Accessibility

**Focus Support:**
- All widget classes have `can_focus=True` enabled, making them tabbable
- FileLink receives `_embedded=True` parameter from parent widgets to disable focus and prevent "focus stealing"
- When `_embedded=False` (default), FileLink is a standalone focusable widget
- Focus indicator CSS uses `:focus` pseudo-class with accent color background and border
- Tab/Shift+Tab navigation works automatically for all focusable widgets

**Keyboard Bindings:**
- Implemented using Textual's `BINDINGS` class variable (list of `Binding` objects)
- Each binding maps: `Binding(key, action_name, description, show=False)`
- Actions are defined as `action_*` methods in the widget class
- Bindings use `show=False` to hide from help screen (keyboard shortcuts are context-specific)
- Customizable by subclassing and overriding `BINDINGS`:

```python
from textual.binding import Binding
from textual_filelink import FileLink

class CustomFileLink(FileLink):
    BINDINGS = [
        Binding("enter", "open_file", "Open"),      # Use Enter instead of 'o'
        Binding("ctrl+o", "open_file", "Open"),     # Add Ctrl+O
    ]
```

**Widget-Level Actions:**

*FileLink:*
- `action_open_file()` - Opens file in configured editor (default: VSCode)

*FileLinkWithIcons:*
- `action_open_file()` - Delegates to child FileLink
- `action_icon_1()` through `action_icon_9()` - Activates clickable icons by index (1st through 9th)

*ToggleableFileLink:*
- `action_open_file()` - Delegates to child FileLink
- `action_toggle()` - Toggles checkbox, posts `Toggled` message
- `action_remove()` - Posts `Removed` message if removal enabled
- `action_icon_1()` through `action_icon_9()` - Activates clickable icons by index (1st through 9th)

*CommandLink:*
- `action_open_output()` - Opens output file if it exists
- `action_play_stop()` - Toggles between play/stop states
  - Posts `PlayClicked` if not running, `StopClicked` if running
- `action_settings()` - Opens settings, posts `SettingsClicked` message
- `action_toggle()` - Inherited from ToggleableFileLink (uses `priority=True` binding)
- `action_remove()` - Inherited from ToggleableFileLink (uses `priority=True` binding)

**Built-in Bindings:**

*FileLink:*
- `enter`, `o` - Open file

*FileLinkWithIcons:*
- `enter`, `o` - Open file
- `1`-`9` - Activate clickable icons (1st through 9th)

*ToggleableFileLink:*
- `enter`, `o` - Open file
- `space`, `t` - Toggle checkbox
- `delete`, `x` - Remove widget
- `1`-`9` - Activate clickable icons (1st through 9th)

*CommandLink:*
- `enter`, `o` - Open output file
- `space`, `p` - Play/Stop command
- `s` - Settings dialog
- `t`, `delete`, `x` - Toggle/Remove (inherited, with priority override)

**App-Level Dynamic Bindings:**

Widgets don't know their position in a list, so apps should handle positional key bindings:

```python
from textual.app import App
from textual import events
from textual_filelink import CommandLink

class MyApp(App):
    def compose(self):
        with ScrollableContainer():
            yield CommandLink("Build")   # Press 1
            yield CommandLink("Test")    # Press 2
            yield CommandLink("Deploy")  # Press 3

    def on_key(self, event: events.Key) -> None:
        """Route number keys 1-9 to activate specific commands."""
        if event.key.isdigit():
            num = int(event.key)
            commands = list(self.query(CommandLink))
            if 0 < num <= len(commands):
                cmd = commands[num - 1]
                # Trigger play action
                cmd.action_play_stop()
                event.prevent_default()
```

**Tooltip Enhancement:**
- All tooltips automatically include keyboard shortcut hints for discoverability
- Format: `"<description> (<key>)"` or `"<description> (<key1>/<key2>)"` for multiple keys
- Implementation: `_get_keys_for_action()` and `_enhance_tooltip()` helper methods
- Enhancement happens dynamically based on widget's BINDINGS
- Respects custom BINDINGS overrides - tooltips automatically adapt when subclassed
- Examples:
  - Toggle: "Click to toggle (space/t)"
  - Remove: "Remove (delete/x)"
  - Icon 1: "Status (1)"
  - Settings: "Settings (s)"
  - Play/Stop: "Run command (space/p)" or "Stop command (space/p)"

**Design Notes:**
- `enter`/`o` for open (Enter is standard, o is mnemonic)
- `space`/`t` for toggle gives users flexibility (Space is standard, t is mnemonic)
- `delete`/`x` for remove gives users two options
- Number keys 1-9 limited to 9 icons per widget (standard TUI pattern)
- Child FileLink in parent widgets uses `_embedded=True` to avoid focus conflicts
- `priority=True` binding flag overrides parent class bindings
- Settings and play_stop icons use action names not numbers for tooltip enhancement

### Event Handling
- All click handlers call `event.stop()` to prevent event bubbling at interaction points
- Widget-specific messages bubble up by default, allowing parent containers to handle them

### Icon Updates
The `update_icon()` method re-renders all icons:
- Call `_render_icons()` to rebuild the layout
- This is necessary because icons are Static widgets, not simple text properties

### Async/Threading Considerations
- All widget operations are sync (no async methods except test fixtures)
- Long-running operations (opening editors) use timeout to avoid blocking
  - **Important**: If a timeout is used anywhere in the codebase, use **40 seconds (40s)** as the standard timeout value
- For CommandLink, use `app.run_worker()` to run async command execution

### Command Execution
- Uses subprocess with timeout, environment copy, and cwd preservation
- Failures are caught and displayed via `app.notify()`
- No direct terminal interaction; all output goes through notifications

## Configuration Files

- **pyproject.toml**: Project metadata, dependencies, tool configuration
- **.github/workflows/ci.yml**: CI pipeline (tests on push/PR to main)
- **.ruff_cache/, htmlcov/**: Generated during development (ignore)
- **.coverage**: Coverage data file (ignore)
- **refactor-2025-12-22.md**: Detailed v0.4.0 architecture plan (composition over inheritance)

## Future Architecture (v0.4.0 - Planned)

See `refactor-2025-12-22.md` for the complete v0.4.0 architecture plan. Key changes:

1. **ToggleableFileLink deprecated** - Use `FileLinkWithIcons` + `FileLinkList` instead
2. **CommandLink rewritten** - Will inherit from `Horizontal` (not ToggleableFileLink) with flat layout
3. **Composition over inheritance** - Cleaner separation of concerns
4. **Breaking changes** - Pre-1.0 allows breaking changes for better design

## Notes for Future Development

1. **Icon System**: The dynamic icon rendering is complex. Always re-render when icons change via `_render_icons()`.
2. **Message Handlers**: When adding new message types, remember to initialize their attributes in `__init__()`.
3. **CSS**: Default CSS is defined in class-level `DEFAULT_CSS` strings. Custom CSS can be set on the app.
4. **Dependencies**: Keep textual version requirement at `>=6.11.0` to ensure compatibility.
5. **Python Version**: Support Python 3.9+ (check in pyproject.toml classifiers).
6. **Version Compatibility**: When implementing v0.4.0 changes, maintain backwards compatibility where possible or provide clear migration guides.
