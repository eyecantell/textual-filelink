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

### Event Handling
- All click handlers call `event.stop()` to prevent event bubbling at interaction points
- Widget-specific messages bubble up by default, allowing parent containers to handle them

### Icon Updates
The `update_icon()` method re-renders all icons:
- Call `_render_icons()` to rebuild the layout
- This is necessary because icons are Static widgets, not simple text properties

### Async/Threading Considerations
- All widget operations are sync (no async methods except test fixtures)
- Long-running operations (opening editors) use short timeout (5s) to avoid blocking
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
