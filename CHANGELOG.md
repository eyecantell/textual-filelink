# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-01-03

### Added
- **Logging Infrastructure**: Complete logging system for debugging and diagnostics
  - `setup_logging(level, format_string)` - Enable console logging
  - `disable_logging()` - Remove all handlers
  - `get_logger()` - Get package logger (internal use)
  - NullHandler by default (opt-in logging, library best practice)
  - Compatible with standard Python logging

- **Logging Coverage**: DEBUG/INFO/ERROR logging throughout widgets
  - **FileLink**: Command execution, path resolution, subprocess errors (Priority 1)
  - **FileLinkWithIcons**: Icon validation errors (Priority 2)
  - **FileLinkList**: Item add/remove, ID validation (Priority 2)
  - **CommandLink**: Widget lifecycle, timer intervals, status changes (Priority 3)

### Documentation
- Added comprehensive logging documentation to README.md and CLAUDE.md
- Added `tests/test_logging.py` with full test coverage (96%)

## [0.8.1]

### Added
- **FileLink**: Added `set_path()` method to update the file path after initialization
  - Parameters: `path`, `display_name`, `line`, `column` (all optional except path)
  - Updates internal state, display text, and tooltip
  - Line and column are preserved if not explicitly provided

### Fixed
- **CommandLink**: `set_output_path()` now correctly updates FileLink when called with a new path
  - Previously, changing from one output file to another would not update the clickable link
  - Now handles all state transitions: Static ↔ FileLink and FileLink path updates

## [0.8.0] - 2025-12-28

### Changed
- **BREAKING: CommandLink timer API redesigned** - Now uses timestamps instead of pre-formatted strings
  - **Removed**: `set_timer_data(duration_str, time_ago_str)` method (no deprecation - clean break)
  - **Added**: `set_start_time(timestamp)` and `set_end_time(timestamp)` methods
  - **Added**: `start_time` and `end_time` constructor parameters (float | None)
  - **Added**: `start_time` and `end_time` parameters to `set_status()` for atomic updates
  - Timer now self-contained: computes and formats relative times internally
  - No external polling required: widget manages its own 1-second update interval
  - **Migration**: Replace `set_timer_data(duration_str="12m 34s")` with `set_start_time(time.time())`
  - **Benefits**: Eliminates layering violations, reduces coupling, simplifies external code (80→10 lines in demo)

### Added
- **Public time formatting utilities** - Exported from `textual_filelink`
  - `format_duration(seconds: float) -> str` - Format elapsed time as duration
    - Milliseconds: "500ms" for sub-second durations (< 1s)
    - Decimal seconds: "2.4s" for 1-60s range
    - Compound units: "1m 30s", "2h 5m", "1d 3h", "2w 3d"
  - `format_time_ago(seconds: float) -> str` - Format elapsed time as time-ago
    - Single-unit display: "5s ago", "2m ago", "3h ago", "2d ago", "1w ago"
  - Both functions handle edge cases: negative values return empty string
  - Available for external use: `from textual_filelink import format_duration, format_time_ago`

## [0.7.0] - 2025-12-28

### Added
- **Timer display for CommandLink** - Optional elapsed time and time-ago display
  - New `show_timer` parameter (default: False) - Enable fixed-width timer column
  - New `timer_field_width` parameter (default: 12) - Control timer column width
  - `set_timer_data(duration_str, time_ago_str)` method - Update timer with pre-formatted strings
  - Automatic display switching based on running state:
    - Shows `duration_str` when command is running (e.g., "12m 34s")
    - Shows `time_ago_str` when command is not running (e.g., "5s ago")
  - Auto-updates every 1 second when enabled
  - Right-justified padding for perfect alignment in command lists
  - Example: `CommandLink("Build", show_timer=True)`
  - Designed for integration with textual-cmdorc's RunHandle time formatting
  - New layout: `[status/spinner] [timer?] [▶️/⏹️] command_name [⚙️]`
  - Timer display uses muted text color for visual hierarchy
  - Timer interval automatically started/stopped on mount/unmount
  - Optimized to avoid unnecessary refreshes (only updates when timer string changes)
- Enhanced `demo_04_commandlink.py` with timer examples
  - Section 5 demonstrates timer functionality with live updates
  - "Run Compile (with timer)" and "Run Benchmark (with timer)" buttons
  - Real-time duration and time-ago updates
  - Demonstrates completed state with "2h ago" initialization

## [0.6.0] - 2025-12-26

### Changed
- **BREAKING: CommandLink API renamed for Textual compatibility** - Resolves naming conflict with Textual's widget.name attribute
  - **Property renamed**: `link.name` → `link.command_name` for accessing the command name
  - **Parameter renamed**: `CommandLink(name="Build")` → `CommandLink(command_name="Build")`
  - **Positional args still work**: `CommandLink("Build")` continues to work unchanged
  - **Textual's name parameter now available**: `CommandLink("Build", name="my-widget")` now works
  - Prevents confusion when writing generic widget-handling code
  - Migration for property access: Replace `widget.name` with `widget.command_name`
  - Migration for keyword args: Replace `name=` with `command_name=` (positional unchanged)
  - **Note**: Message attributes are unchanged - `event.name` still works in message handlers

### Fixed
- **FileLinkWithIcons tooltip consistency** - Now correctly uses `FileLink.DEFAULT_OPEN_KEYS` as fallback instead of hardcoded `["enter", "o"]`
  - If users globally change `FileLink.DEFAULT_OPEN_KEYS`, FileLinkWithIcons tooltips now reflect the change
  - Ensures true consistency between FileLink and FileLinkWithIcons keyboard shortcut defaults

## [0.5.0] - 2025-12-26

### Added
- **Custom tooltip support** - CommandLink and FileLinkWithIcons now accept a `tooltip` parameter
  - Custom tooltip text is used as the base description
  - Keyboard shortcuts are automatically appended to the custom tooltip by default
  - If no custom tooltip is provided, defaults to command name (CommandLink) or file name (FileLinkWithIcons)
- **Tooltip control via `append_shortcuts` parameter** - All CommandLink tooltip methods now support controlling keyboard shortcut appending
  - `set_name_tooltip(tooltip, append_shortcuts=True)` - Set command name tooltip with optional shortcut appending
  - `set_play_stop_tooltips(run_tooltip, stop_tooltip, append_shortcuts=True)` - Set play/stop tooltips with optional shortcut appending
  - `set_settings_tooltip(tooltip, append_shortcuts=True)` - Set settings tooltip with optional shortcut appending
  - Defaults to `True` for backward compatibility
  - Allows custom tooltips without keyboard shortcuts when needed (e.g., critical actions, custom formatting)
- New public methods for CommandLink tooltip management:
  - `set_name_tooltip()` - Update command name widget tooltip
  - `set_play_stop_tooltips()` - Update play/stop button tooltips (respects running state)
  - `set_settings_tooltip()` - Update settings icon tooltip
- Enhanced `set_status()` method - Now supports updating all tooltips in one call
  - New parameters: `name_tooltip`, `run_tooltip`, `stop_tooltip`, `append_shortcuts`
  - Convenient for updating status and tooltips together when state changes
  - Example: `link.set_status(running=True, tooltip="Building...", name_tooltip="Build in progress")`
- New helper methods for tooltip building:
  - `_build_tooltip_with_shortcuts()` - Combines custom tooltip with keyboard shortcuts
  - `_get_shortcuts_string()` - Returns formatted keyboard shortcut string
- New demo: `examples/demo_tooltip_control.py` - Demonstrates tooltip control options
- **Auto-ID generation for FileLink and FileLinkWithIcons**
  - IDs now auto-generate from filename using `sanitize_id()` if not provided
  - Example: `FileLink("README.md")` gets `id="readme-md"`
  - Explicit IDs still override auto-generation
  - Consistent with CommandLink behavior
  - Note: If you have multiple widgets with the same filename, provide explicit IDs
- **Custom `open_keys` parameter for FileLinkWithIcons**
  - Same API as FileLink for keyboard shortcut customization
  - Example: `FileLinkWithIcons("file.txt", open_keys=["f2"])`
  - Custom keys are forwarded to the embedded FileLink
  - Tooltips automatically reflect custom keyboard shortcuts
- **Customizable spinner for CommandLink**
  - New `spinner_frames` parameter for custom animation frames
  - New `spinner_interval` parameter for animation speed control
  - Example: `CommandLink("Build", spinner_frames=["◐", "◓", "◑", "◒"], spinner_interval=0.05)`
  - Default spinner uses Braille pattern with 0.1s interval

### Changed
- Improved FileLinkList error messages for duplicate IDs
  - More helpful guidance when ID conflicts occur
  - Suggests using different names or explicit ID parameters
- FileLinkList no longer raises ValueError for FileLink/FileLinkWithIcons without explicit IDs
  - Auto-generated IDs are now used automatically
  - Only widgets without any ID (e.g., Static with no id parameter) will raise an error

### Fixed
- Avoided naming conflict with Textual's internal `_tooltip` attribute by using `_custom_tooltip` internally

### Removed
- **ToggleableFileLink widget** - Removed as planned (deprecated since v0.4.0)
  - Use `FileLinkWithIcons` for icon functionality
  - Use `FileLinkList` for toggle/remove controls
  - Migration: Replace `ToggleableFileLink(path, icons=[...])` with `FileLinkWithIcons(path, icons_before=[...])`
  - For batch operations, wrap widgets in `FileLinkList` with `show_toggles=True`

## [0.4.0] - 2025-12-23

### Added
- **Complete architecture overhaul** - Composition over inheritance throughout
- **FileLinkWithIcons** - New widget for FileLink with customizable icons
  - Icons can be positioned before or after the filename
  - Supports multiple icons with individual tooltips and keyboard shortcuts
  - Uses `Icon` dataclass for type-safe configuration
- **FileLinkList** - New container widget for managing file links
  - Scrollable container (inherits from VerticalScroll)
  - Optional uniform toggle/remove controls for all items
  - Batch operations: `toggle_all()`, `remove_selected()`, `get_toggled_items()`
  - Requires explicit IDs for all items (fail-fast validation)
  - Internal `FileLinkListItem` wrapper for layout management
- **Icon dataclass** - Type-safe icon configuration
  - Required fields: `name`, `icon`
  - Optional: `tooltip`, `clickable`, `key`, `visible`
  - Validation in `__post_init__()`
- **sanitize_id() utility** - Convert names to valid widget IDs
  - Lowercases, converts spaces/paths to hyphens
  - Removes special characters
  - Used internally by CommandLink for auto-ID generation
- **Custom keyboard shortcuts per instance**
  - FileLink: `open_keys` parameter
  - CommandLink: `open_keys`, `play_stop_keys`, `settings_keys` parameters
  - FileLinkWithIcons: Icon-level `key` parameter for custom shortcuts
- **Runtime keyboard binding approach** - Bindings set in `on_mount()` using `self._bindings.bind()`
- **CommandLink improvements**:
  - Rewritten as standalone widget (extends Horizontal, not ToggleableFileLink)
  - Auto-generates ID from command name using `sanitize_id()`
  - Flat layout: `[status/spinner] [▶️/⏹️] name [⚙️?]`
  - `show_settings` parameter (defaults to False)
  - `output_path` parameter for clickable command name
  - `set_output_path()` method to update output path dynamically
- **FileLink improvements**:
  - `display_name` parameter (defaults to filename)
  - `FileLink.Opened` message (replaces `Clicked` with better semantics)
  - `_embedded` parameter to disable focus when nested in parent widgets
  - `tooltip` parameter for custom tooltip text
- **Demo applications** - New comprehensive examples:
  - `demo_01_filelink.py` - Basic FileLink usage
  - `demo_02_filelink_with_icons.py` - Icon configurations
  - `demo_03_filelink_list.py` - List container with batch operations
  - `demo_04_commandlink.py` - Command orchestration
  - `demo_05_dev_orchestration.py` - Complete dev workflow example
- **Python version support** - Now supports Python 3.9-3.13
- **Enhanced documentation**:
  - Complete API reference in README
  - Architecture documentation in refactor-2025-12-22.md
  - Comprehensive CLAUDE.md for AI assistance

### Changed
- **Breaking**: CommandLink no longer inherits from ToggleableFileLink
  - Now a standalone widget with flat composition
  - Messages only include `name` and `output_path` (no `is_toggled`)
  - Toggle/remove controls managed by FileLinkList instead
- **Breaking**: FileLinkList requires explicit IDs for all items
  - Raises ValueError if item has no ID
  - Raises ValueError on duplicate IDs
  - CommandLink auto-generates IDs, but FileLink requires manual ID
- **Breaking**: FileLink.Clicked message renamed to FileLink.Opened
  - FileLink.Clicked kept as backwards-compatible alias (will be removed in future)
  - Better semantic meaning (file is opened, not just clicked)
- Reorganized pyproject.toml for better clarity
- Test coverage maintained at 90%+

### Deprecated
- `FileLink.Clicked` message - Use `FileLink.Opened` instead (backwards-compatible alias)

### Preserved
- **ToggleableFileLink** widget - Kept for backwards compatibility (was planned for removal)
  - Still uses `IconConfig` dataclass (not the new `Icon` class)
  - Standalone widget with toggle, icons, and remove controls
  - Useful when FileLinkList is not needed

### Fixed
- CommandLink widget ID validation errors
- Scrolling issues in demo applications
- Various edge cases in error handling

[Unreleased]: https://github.com/eyecantell/textual-filelink/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/eyecantell/textual-filelink/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/eyecantell/textual-filelink/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/eyecantell/textual-filelink/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/eyecantell/textual-filelink/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/eyecantell/textual-filelink/compare/v0.3.0...v0.4.0

## [0.3.0] - 2025-12-16

### Added
- **Full keyboard accessibility** - All widgets are now fully navigable and operable without a mouse
  - All three widget classes (`FileLink`, `ToggleableFileLink`, `CommandLink`) now support `can_focus=True` for Tab navigation
  - Comprehensive keyboard shortcuts via `BINDINGS` class variable
  - Focus indicators with CSS `:focus` pseudo-class styling (accent color background and border)
  - `_embedded` parameter for `FileLink` to prevent focus stealing when nested in parent widgets
- **Keyboard shortcuts for FileLink**:
  - `o` - Open file in editor
- **Keyboard shortcuts for ToggleableFileLink**:
  - `o` - Open file
  - `space` or `t` - Toggle checkbox
  - `delete` or `x` - Remove widget
  - `1-9` - Activate clickable icons (in order of appearance)
- **Keyboard shortcuts for CommandLink**:
  - `o` - Open output file
  - `space` or `p` - Play/Stop command
  - `s` - Settings dialog
  - `t` - Toggle checkbox
  - `delete` or `x` - Remove widget
- **Automatic tooltip enhancement** - All tooltips now include keyboard shortcut hints for discoverability
  - Format: `"<description> (<key>)"` or `"<description> (<key1>/<key2>)"` for multiple keys
  - Dynamically adapts when `BINDINGS` are customized in subclasses
  - Special handling for settings and play_stop icons
- **Customizable keyboard shortcuts** - Override `BINDINGS` class variable in subclasses to customize keys
- **Action methods** for programmatic keyboard action triggering:
  - `FileLink.action_open_file()`
  - `ToggleableFileLink.action_open_file()`, `action_toggle()`, `action_remove()`, `action_icon_1()` through `action_icon_9()`
  - `CommandLink.action_open_output()`, `action_play_stop()`, `action_settings()`, `action_toggle()`, `action_remove()`
- **Comprehensive test suite** for keyboard accessibility (tests/test_tooltip_enhancement.py with 405 lines)
- **CLAUDE.md** - Project guidance document for AI assistants with detailed implementation notes

### Changed
- Test coverage minimum lowered to 90% (from previous threshold)
- Improved overall test coverage to 94.13%
- Updated README with comprehensive keyboard accessibility documentation
- Enhanced tooltips now show keyboard shortcuts automatically

### Fixed
- CommandLink widget ID validation errors
- Remove button functionality in demo_07
- Scrolling issues in demo_07
- Various edge cases in error handling (non-existent files, permission errors, symlinks, subprocess failures)

[0.3.0]: https://github.com/eyecantell/textual-filelink/compare/v0.2.0...v0.3.0

## [0.2.0] - 2025-11-28

### Added
- **Multiple icons support** for `ToggleableFileLink` - display multiple status icons per file instead of just one
- `IconConfig` dataclass for type-safe icon configuration with properties:
  - `name` (str, required): Unique identifier for the icon
  - `icon` (str, required): Unicode character to display
  - `position` (str): "before" or "after" the filename (default: "before")
  - `index` (int | None): Explicit ordering index for controlling display order
  - `visible` (bool): Whether icon is initially visible (default: True)
  - `clickable` (bool): Whether icon posts `IconClicked` messages (default: False)
  - `tooltip` (str | None): Tooltip text (default: None)
- New `icons` parameter accepts list of `IconConfig` dataclasses or dicts
- Icon positioning control - place icons before or after the filename
- Explicit icon ordering via `index` property, with automatic ordering for icons without indices
- Smart icon sorting: explicit indices first (sorted by index then name), followed by auto-assigned indices (maintaining list order)
- `IconClicked` message (replaces `StatusIconClicked`) posted when clickable icons are activated
- Dynamic icon manipulation methods:
  - `set_icon_visible(name, visible)` - show/hide specific icons
  - `update_icon(name, **kwargs)` - update any icon property dynamically
  - `get_icon(name)` - retrieve icon configuration as a dict copy
- Comprehensive validation for icon configurations with helpful error messages
- Full test coverage for multi-icon functionality (83 tests total, all passing)

### Changed
- `StatusIconClicked` message renamed to `IconClicked` for clarity (contains `icon_name` and `icon` properties)
- Icon click event now includes `icon_name` parameter to identify which icon was clicked
- Internal icon handling rewritten to support multiple icons with dynamic updates
- Async `_recompose_icons()` method for safe DOM manipulation when icon order changes

### Deprecated
- `status_icon` parameter - use `icons=[{"name": "status", "icon": "✓"}]` instead
- `status_icon_clickable` parameter - use `icons=[{"name": "status", "icon": "✓", "clickable": True}]` instead  
- `status_tooltip` parameter - use `icons=[{"name": "status", "icon": "✓", "tooltip": "text"}]` instead
- Old parameters still work with deprecation warnings for backwards compatibility

### Migration Guide

**Old API (still works with deprecation warning):**
```python
ToggleableFileLink(
    path,
    status_icon="✓",
    status_icon_clickable=True,
    status_tooltip="Validated"
)
```

**New API:**
```python
ToggleableFileLink(
    path,
    icons=[{
        "name": "status",
        "icon": "✓",
        "clickable": True,
        "tooltip": "Validated"
    }]
)
```

**Multiple icons example:**
```python
ToggleableFileLink(
    path,
    icons=[
        {"name": "status", "icon": "✓", "position": "before", "tooltip": "Valid"},
        {"name": "lock", "icon": "🔒", "position": "after", "tooltip": "Read-only"},
        {"name": "modified", "icon": "📝", "clickable": True, "tooltip": "Click to view changes"}
    ]
)
```

**Handling icon click events:**
```python
# Old
def on_toggleable_file_link_status_icon_clicked(self, event):
    self.notify(f"Clicked {event.icon}")

# New  
def on_toggleable_file_link_icon_clicked(self, event):
    self.notify(f"Clicked {event.icon_name}: {event.icon}")
```

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- `FileLink` widget for clickable file links that open in your editor
- `ToggleableFileLink` widget with optional toggle and remove controls
- Single status icon support
- Support for VSCode, vim, nano, Eclipse, and custom editor commands
- Line and column navigation support
- Comprehensive test suite
- Full documentation and examples

[0.2.0]: https://github.com/eyecantell/textual-filelink/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/eyecantell/textual-filelink/releases/tag/v0.1.0