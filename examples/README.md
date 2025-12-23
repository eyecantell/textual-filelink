# textual-filelink Examples

This directory contains example applications demonstrating the features of textual-filelink.

## Running Examples

From the repository root:

```bash
# Run from the examples directory (recommended)
cd examples
pdm run python demo_01_filelink.py

# Or run from repository root
pdm run python examples/demo_01_filelink.py
```

## Available Examples

### demo_01_filelink.py
Demonstrates FileLink - the foundation widget for clickable file links.

**Features:**
- Basic clickable file links
- Line and column navigation
- Built-in editor support (VSCode, Vim, Nano, Eclipse)
- Custom editor configuration
- Keyboard shortcuts (enter/o to open files)

**Run:** `python demo_01_filelink.py`

### demo_02_filelink_with_icons.py
Demonstrates FileLinkWithIcons - file links with visual status and metadata icons.

**Features:**
- Icons before and after filenames
- Clickable icons with event handling
- Dynamic icon updates and visibility toggling
- File type indicators (🐍/📊/⚙️)
- Status badges (✅/❌/⚠️/⏳)
- Keyboard shortcuts for icon activation

**Run:** `python demo_02_filelink_with_icons.py`

### demo_03_filelink_list.py
Demonstrates FileLinkList - a container for managing file link widgets with batch operations.

**Features:**
- Toggle checkboxes for selection
- Remove buttons for deletion
- Batch operations (toggle all, remove selected, clear all)
- ID validation (required and unique)
- Mixed widget types (FileLink + FileLinkWithIcons)
- Live statistics and event handling

**Run:** `python demo_03_filelink_list.py`

---

More examples coming soon:
- `demo_04_commandlink.py` - CommandLink for command orchestration

## Sample Files

The `sample_files/` directory contains test files used by the examples. These files demonstrate:
- Different file types (Python, JSON, Markdown, CSV, etc.)
- Line and column navigation
- Multiple file formats for testing editor integration
