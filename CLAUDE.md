# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**textual-filelink** is a Python library providing clickable file link widgets for [Textual](https://github.com/Textualize/textual) TUI applications. It enables opening files in editors directly from terminal UIs with support for line/column navigation, customizable icons, toggle controls, and command orchestration.

The library exports three main widget classes:
- **FileLink**: Basic clickable filename link
- **ToggleableFileLink**: FileLink with checkboxes, custom icons, and removal capability
- **CommandLink**: Specialized widget for command orchestration with status icons and play/stop controls

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
# Run demo applications (various examples in scripts/)
pdm run python scripts/demo_01_basic_filelink.py
pdm run python scripts/demo_06_commandlink_simple.py
pdm run python scripts/demo_07_async_orchestration.py

# Run textual dev mode (hot-reload for demo development)
pdm run textual-dev run scripts/demo_01_basic_filelink.py

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

## Architecture Overview (v0.4.0)

### Core Widget Hierarchy
```
v0.4.0 Architecture (Composition over Inheritance):

Static (Textual)
  └─ FileLink (basic clickable file link)

Horizontal (Textual)
  └─ FileLinkWithIcons (FileLink + icons via composition)

Horizontal (Textual)
  └─ CommandLink (flat widget, no inheritance)
       Uses: FileLink (for name), Static widgets (for controls)

VerticalScroll (Textual)
  └─ FileLinkList (container for uniform controls)
       Contains: FileLinkListItem wrappers
         └─ Any widget (FileLink, FileLinkWithIcons, CommandLink, etc.)

Legacy (backward compatibility):
  └─ ToggleableFileLink (inheritance-based, deprecated in v0.4.0)
```

### FileLink (src/textual_filelink/file_link.py)
- **Responsibility**: Render a clickable filename that opens a file in an editor
- **Key Features**:
  - Custom `display_name` parameter (defaults to filename)
  - Runtime keyboard bindings via `open_keys` parameter
  - Supports multiple editor command builders (VSCode, Vim, Nano, Eclipse)
  - Shows notifications on success/failure
  - Default is VSCode with `code --goto file:line:column`
- **Message**: `FileLink.Opened` (path, line, column) - **Breaking change**: renamed from `Clicked` in v0.4.0
- **Keyboard Shortcuts**: Customizable via `open_keys` parameter (default: `["o"]`)

### FileLinkWithIcons (src/textual_filelink/file_link_with_icons.py)
- **Responsibility**: Compose FileLink with custom icons via composition (not inheritance)
- **Key Concepts**:
  - Uses `Icon` dataclass for type-safe icon configuration
  - Icons positioned via `icons_before` and `icons_after` lists
  - Layout: `[icons_before...] FileLink [icons_after...]`
  - Dynamic keyboard shortcuts for clickable icons (1-9 keys)
  - Runtime bindings created in `on_mount()` using `self._bindings.bind()`
- **Messages**:
  - `FileLinkWithIcons.IconClicked` (path, icon_name, icon_char)
  - Plus `FileLink.Opened` from embedded FileLink
- **Properties**: `file_link` property provides access to internal FileLink widget

### CommandLink (src/textual_filelink/command_link.py)
- **Responsibility**: Orchestrate command execution with status display and controls
- **Key Concepts**:
  - **Flat architecture**: Inherits from `Horizontal`, not from ToggleableFileLink
  - Builds own layout with child widgets (no inheritance complexity)
  - Layout: `[status/spinner] [▶️/⏹️] command_name [⚙️?]`
  - Animated spinner using `set_interval()` when running
  - Auto-generates widget ID from command name via `sanitize_id()`
  - Runtime keyboard bindings: `open_keys`, `play_stop_keys`, `settings_keys`
  - Internal attribute naming: `_command_running` (not `_running` to avoid Textual's MessagePump conflict)
- **Messages**:
  - `CommandLink.PlayClicked` (name, output_path)
  - `CommandLink.StopClicked` (name, output_path)
  - `CommandLink.SettingsClicked` (name, output_path)
  - `CommandLink.OutputClicked` (output_path)
- **Breaking Changes from v0.3.x**:
  - No `show_toggle` or `show_remove` parameters (use FileLinkList instead)
  - Constructor signature changed (keyword-only `output_path`)
  - No inheritance from ToggleableFileLink

### FileLinkList (src/textual_filelink/file_link_list.py)
- **Responsibility**: Container for managing widgets with uniform toggle/remove controls
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

### Utility Functions (src/textual_filelink/utils.py)
- `sanitize_id(name: str) -> str` - Convert any string to valid widget ID
  - Lowercases, converts spaces/paths to hyphens, removes special chars

## Testing Structure

- **tests/conftest.py**: Shared fixtures for all tests
- **tests/test_file_link.py**: FileLink unit tests
- **tests/test_toggleable_file_link.py**: ToggleableFileLink unit tests
- **tests/test_command_link.py**: CommandLink unit tests
- **tests/test_tooltip_enhancement.py**: Tooltip keyboard shortcut enhancement tests
- **tests/test_integration.py**: Integration tests with mock Textual apps

**Key Testing Pattern**: Tests use `pilot` fixture to simulate user interactions (clicks) and verify message emission.

### Pytest Configuration
- Coverage minimum: 90% (enforced in CI)
- Async mode: auto
- Fixtures: asyncio fixtures with function-level scope
- Markers: `@pytest.mark.slow`, `@pytest.mark.integration` available

## Important Implementation Details

### Keyboard Accessibility

**Focus Support:**
- All three widget classes have `can_focus=True` enabled, making them tabbable
- FileLink receives `_embedded=True` parameter from parent widgets (ToggleableFileLink/CommandLink) to disable focus and prevent "focus stealing"
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

*ToggleableFileLink:*
- `action_open_file()` - Delegates to child FileLink
- `action_toggle()` - Toggles checkbox, posts `Toggled` message
- `action_remove()` - Posts `Removed` message if removal enabled
- `action_icon_1()` through `action_icon_9()` - Activates clickable icons by index (1st through 9th)
  - Uses helper method `_activate_icon_by_index()` to find and activate icons
  - Only activates icons with `clickable=True`
  - Posts `IconClicked` message with icon name and content

*CommandLink:*
- `action_open_output()` - Opens output file if it exists
- `action_play_stop()` - Toggles between play/stop states
  - Posts `PlayClicked` if not running, `StopClicked` if running
- `action_settings()` - Opens settings, posts `SettingsClicked` message
- `action_toggle()` - Inherited from ToggleableFileLink (uses `priority=True` binding)
- `action_remove()` - Inherited from ToggleableFileLink (uses `priority=True` binding)

**Built-in Bindings:**

*FileLink:*
- `o` - Open file

*ToggleableFileLink:*
- `o` - Open file
- `space`, `t` - Toggle checkbox
- `delete`, `x` - Remove widget
- `1`-`9` - Activate clickable icons (1st through 9th)

*CommandLink:*
- `o` - Open output file
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
  - Settings: "Settings (s)" (special case, uses action name not icon number)
  - Play/Stop: "Run command (space/p)" or "Stop command (space/p)"

**Design Notes:**
- `o` for open instead of Enter/Space to avoid conflicts with scrolling/form submission
- `space`/`t` for toggle gives users flexibility (Space is standard, t is mnemonic)
- `delete`/`x` for remove gives users two options
- Number keys 1-9 limited to 9 icons per widget (standard TUI pattern)
- Child FileLink in ToggleableFileLink/CommandLink uses `_embedded=True` to avoid focus conflicts
- `priority=True` binding flag in CommandLink overrides parent class bindings
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

## Notes for Future Development

1. **Icon System**: The dynamic icon rendering is complex. Always re-render when icons change via `_render_icons()`.
2. **Message Handlers**: When adding new message types, remember to initialize their attributes in `__init__()`.
3. **CSS**: Default CSS is defined in class-level `DEFAULT_CSS` strings. Custom CSS can be set on the app.
4. **Dependencies**: Keep textual version requirement at `>=6.11.0` to ensure compatibility.
5. **Python Version**: Support Python 3.9+ (check in pyproject.toml classifiers).
