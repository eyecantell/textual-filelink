# textual-filelink Demo Examples

This directory contains demo TUI applications that showcase the features and capabilities of the textual-filelink library.

## Learning Path

Start with the beginner examples and progress at your own pace. Each demo is self-contained and can run independently.

### Beginner Examples (Start Here!)

1. **[demo_01_basic_filelink.py](demo_01_basic_filelink.py)** - Learn FileLink Basics
   - Clickable file links in a TUI
   - Opening files in your editor
   - Line and column navigation
   - Handling click events
   - **Best for:** Understanding what FileLink does and why it's useful

2. **[demo_02_toggleable_basics.py](demo_02_toggleable_basics.py)** - Add Toggle and Remove Controls
   - Toggle (checkbox) controls for file selection
   - Remove (delete) buttons for file management
   - Showing and hiding controls
   - Handling toggle and remove events
   - Using tooltips for helpful hints
   - **Best for:** Building file selection interfaces

3. **[demo_03_icons_simple.py](demo_03_icons_simple.py)** - Add Status Icons
   - Multiple icons per file link
   - Icon positioning (before/after filename)
   - Making icons clickable
   - Changing icon appearance dynamically
   - **Best for:** Adding visual feedback with icons

### Intermediate Examples (Coming Soon!)

4. **demo_04_icons_advanced.py** - Master the Icon System
   - Advanced icon configuration
   - Icon visibility toggling
   - Icon ordering and positioning
   - Interactive icon demonstrations

5. **demo_05_state_management.py** - Build Stateful File UIs
   - State management patterns
   - Multi-column file selection
   - DataClass patterns for state
   - Refreshing UI based on state changes

6. **demo_06_commandlink_simple.py** - Introduce CommandLink
   - Play/stop buttons
   - Status indicators
   - Simple command simulation
   - Understanding CommandLink basics

### Advanced Examples (Coming Later)

7. **demo_07_commandlink_advanced.py** - Command Orchestration
   - Complex command workflows
   - Batch operations
   - Elapsed time tracking
   - Output file generation

8. **demo_08_custom_editor.py** - Editor Configuration
   - Built-in editor support (VSCode, vim, nano)
   - Custom editor configuration
   - Copy-to-clipboard functionality

9. **demo_09_file_browser.py** - Real File Browser
   - Directory tree navigation
   - File filtering and search
   - Icon-based file type identification
   - Real-world file browsing patterns

10. **demo_10_datatable_integration.py** - DataTable Integration
    - FileLink in DataTable cells
    - Mixed content tables
    - Status indicators in tables

11. **demo_11_error_handling.py** - Error Handling Patterns
    - Validation before opening files
    - Graceful error handling
    - User-friendly error messages

## Quick Reference

Looking for a specific feature? Here's where to find it:

| Want to...                    | Go to...          |
|-------------------------------|-------------------|
| Click and open files          | demo_01           |
| Select/deselect files         | demo_02           |
| Add status icons              | demo_03           |
| Master icon system            | demo_04           |
| Manage file state             | demo_05           |
| Run commands                  | demo_06           |
| Orchestrate multiple commands | demo_07           |
| Configure different editors   | demo_08           |
| Browse directories            | demo_09           |
| Show files in a table         | demo_10           |
| Handle errors gracefully      | demo_11           |

## Running Demos

Each demo is a standalone Python script. To run any demo:

```bash
cd scripts/
python demo_01_basic_filelink.py
```

Or from the project root:

```bash
python scripts/demo_01_basic_filelink.py
```

## Demo Data

All demos use files from the `sample_files/` directory. This ensures:

- **Portability:** Demos work on any system without hardcoded paths
- **Consistency:** All demos use the same test data
- **Reliability:** No dependency on external files or directories

Sample files include:
- `example.py` - Python source file
- `config.json` - JSON configuration
- `data.csv` - CSV data
- `notes.txt` - Text file
- `Makefile` - Make build file
- `LICENSE` - License file

## Tips for Learning

1. **Read the docstring** - Each demo has a clear explanation of what it demonstrates
2. **Look at the comments** - Inline comments explain key concepts
3. **Try modifications** - Experiment by changing the code
4. **Run step by step** - Use the progression from demo_01 to demo_03, then evaluate
5. **Check the README** - The main [README.md](../README.md) has comprehensive documentation

## Structure of Each Demo

Every demo follows a consistent structure:

```python
"""Docstring explaining what this demo demonstrates and why it matters."""

from textual.app import App, ComposeResult
# ... imports ...

class DemoApp(App):
    """The main application."""

    CSS = """..."""  # Styling

    def compose(self) -> ComposeResult:
        """Create the UI."""
        # ... widgets ...

    def on_mount(self) -> None:
        """Set up after mounting."""
        # ... initialization ...

    def on_*_event(self, event) -> None:
        """Handle events from widgets."""
        # ... event handlers ...

if __name__ == "__main__":
    DemoApp().run()
```

## Keyboard Shortcuts

Most demos respond to standard terminal shortcuts:

- `Tab` - Move focus between widgets
- `Ctrl+C` - Exit the application
- `Enter` / `Space` - Activate buttons and controls
- `Q` - Quick exit (when implemented)

## Troubleshooting

### Demo won't start
Make sure you're in the scripts/ directory and have textual installed:
```bash
pip install textual
```

### Demo looks weird/rendering issues
Try updating textual:
```bash
pip install --upgrade textual
```

### Sample files not found
Make sure `sample_files/` directory exists in the scripts/ folder:
```bash
ls scripts/sample_files/
```

## Next Steps

After exploring the foundation demos (01-03):

1. Evaluate which features matter most to you
2. Try modifying the demos to add your own features
3. Refer back to the main [README.md](../README.md) for full API documentation
4. Check the source code in `src/textual_filelink/` for implementation details

## Contributing

Found a bug in a demo? Want to suggest improvements? Please open an issue or pull request on GitHub!

## Resources

- **Main README:** [textual-filelink](../README.md)
- **Textual Documentation:** https://textual.textualize.io/
- **Source Code:** [src/textual_filelink/](../src/textual_filelink/)
- **Tests:** [tests/](../tests/)
