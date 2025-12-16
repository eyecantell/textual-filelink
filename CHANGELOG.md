# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.3.0]: https://github.com/eyecantell/textual-filelink/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/eyecantell/textual-filelink/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/eyecantell/textual-filelink/releases/tag/v0.1.0