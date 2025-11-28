# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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