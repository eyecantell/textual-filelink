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
# Run the demo application
pdm run python src/textual_filelink/demo.py

# Run textual dev mode (hot-reload for demo development)
pdm run textual-dev run src/textual_filelink/demo.py

# Build distribution package
pdm build
```

## Architecture Overview

### Core Widget Hierarchy
```
Static (Textual)
  └─ FileLink
       └─ ToggleableFileLink
            └─ CommandLink
```

### FileLink (src/textual_filelink/file_link.py)
- **Responsibility**: Render a clickable filename that opens a file in an editor
- **Key Features**:
  - Handles click events to open files via subprocess
  - Supports multiple editor command builders (VSCode, Vim, Nano, Eclipse)
  - Customizable command builder for any editor
  - Shows notifications on success/failure
  - Default is VSCode with `code --goto file:line:column`
- **Message**: `FileLink.Clicked` (path, line, column)

### ToggleableFileLink (src/textual_filelink/toggleable_file_link.py)
- **Responsibility**: Extend FileLink with toggle checkboxes, custom icons, and removal
- **Key Concepts**:
  - **Icon System**: Flexible icon configuration with positioning (before/after), visibility control, clickability, and ordering by index
  - **Icon Configuration**: Each icon is a dict with keys: `name`, `icon`, `position`, `index`, `visible`, `clickable`, `tooltip`
  - **Layout**: `[toggle] [icons...] filename [icons...] [remove]`
  - Composed using `Horizontal` container with child Static widgets for each icon
- **Messages**:
  - `ToggleableFileLink.Toggled` (path, is_toggled)
  - `ToggleableFileLink.Removed` (path)
  - `ToggleableFileLink.IconClicked` (path, icon_name, icon)

### CommandLink (src/textual_filelink/command_link.py)
- **Responsibility**: Orchestrate command execution with status display and controls
- **Key Concepts**:
  - Extends ToggleableFileLink with play/stop buttons and animated spinner
  - Displays status icon that animates when `running=True`
  - Uses internal `AnimatedSpinner` widget for animation
  - Layout: `[toggle] [status/spinner] [play] command_name [settings] [remove]`
  - Inherits all toggle/icon functionality from ToggleableFileLink
- **Messages**:
  - `CommandLink.PlayClicked` (name, path, output_path, is_toggled)
  - `CommandLink.StopClicked` (name, path, output_path, is_toggled)
  - `CommandLink.SettingsClicked` (name, path, output_path, is_toggled)
  - Plus inherited from ToggleableFileLink

### Icon Rendering Pattern
Icons are dynamically rendered based on configuration state:
1. Filter icons by visibility
2. Sort by position (before/after), then by explicit index or list order
3. Render each as a Static widget with class `status-icon` (and `clickable` if applicable)
4. Store original configuration in `_icons` list, not widget state

## Testing Structure

- **tests/conftest.py**: Shared fixtures for all tests
- **tests/test_file_link.py**: FileLink unit tests
- **tests/test_toggleable_file_link.py**: ToggleableFileLink unit tests
- **tests/test_command_link.py**: CommandLink unit tests
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
4. **Dependencies**: Keep textual version requirement at `>=6.6.0` to ensure compatibility.
5. **Python Version**: Support Python 3.9+ (check in pyproject.toml classifiers).
