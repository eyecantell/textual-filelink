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

### Intermediate Examples (Build Real Functionality!)

4. **[demo_04_icons_advanced.py](demo_04_icons_advanced.py)** - Master the Icon System
   - Icon ordering with explicit indices
   - Multiple icons at before/after positions
   - Icon visibility toggling with controls
   - Interactive icon workflows (processing, cascading states)
   - Simulated async operations with timers
   - **Best for:** Creating complex visual feedback systems

5. **[demo_05_state_management.py](demo_05_state_management.py)** - Build Stateful File UIs
   - Dataclass-based state tracking
   - Multi-column layout with state synchronization
   - Refreshing UI from state changes
   - Practical file workflow patterns (select, archive, restore)
   - Priority-based file organization
   - **Best for:** Building file management applications

6. **[demo_06_commandlink_simple.py](demo_06_commandlink_simple.py)** - Introduce CommandLink
   - CommandLink widget basics (play/stop buttons)
   - Simple status indicators and updates
   - Timer-based command simulation (synchronous)
   - CommandLink event handling (PlayClicked, StopClicked, SettingsClicked)
   - Output file path concept
   - **Best for:** Understanding command execution patterns before async

### Advanced Examples (Complex Patterns!) ✅

These demos require deeper understanding of async patterns, event handling, and application architecture.

7. **[demo_07_async_orchestration.py](demo_07_async_orchestration.py)** - Simplified Async Command Orchestration ✅
   - asyncio.create_task() for background execution
   - Proper CancelledError handling and cleanup
   - Timer-based elapsed time tracking
   - Batch operations on selected commands
   - Simple output file generation
   - **Prerequisites:** Understand demo_06 and basic async/await

8. **[demo_08_editor_config.py](demo_08_editor_config.py)** - Custom Editor Configuration ✅
   - All 5 built-in editors (VSCode, Vim, Nano, Eclipse, Copy Path)
   - Custom command builder examples (Sublime, IntelliJ, Emacs)
   - Environment variable detection ($EDITOR)
   - Auto-detection with fallback chain
   - Per-instance vs class-level configuration
   - **Prerequisites:** Understand demo_01 FileLink basics

9. **[demo_09_file_browser.py](demo_09_file_browser.py)** - Real File Browser with Navigation ✅
   - Single directory view with file listings
   - 20+ file type icons (emoji-based)
   - Click directories to navigate
   - Parent directory (..) support
   - File filtering by pattern (*.py, test_*.py)
   - Selection with checkboxes
   - **Prerequisites:** Understand demo_05 state management

10. **[demo_10_datatable_files.py](demo_10_datatable_files.py)** - DataTable Integration ✅
    - Files displayed in table format
    - Columns: Icon, Name, Size, Type, Status
    - Human-readable file sizes
    - Status indicators (✅ Valid, ⚠️ Large, 🔒 Locked)
    - Click row to open file
    - **Prerequisites:** Basic Textual DataTable knowledge

11. **[demo_11_error_handling.py](demo_11_error_handling.py)** - Error Handling Patterns ✅
    - Reusable validation helper functions
    - Common error scenarios gallery (10 examples)
    - User-friendly error messages with suggestions
    - Symlink handling (broken link detection)
    - Large file warnings
    - Editor availability validation
    - **Prerequisites:** Understand demo_01 and basic file operations

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

## Learning Path Progression

### Foundation (Demos 01-03)
Master the basics before moving to intermediate examples:
1. **demo_01**: Understand FileLink and file clicking
2. **demo_02**: Add toggle and remove controls
3. **demo_03**: Learn about icons and status indicators

### Intermediate (Demos 04-06)
Build real-world patterns with progressive complexity:
4. **demo_04**: Master advanced icon system (3-5 hours)
5. **demo_06**: Learn CommandLink basics without async (4-6 hours)
6. **demo_05**: Tackle state management and multi-column UIs (6-8 hours)

### Advanced (Demos 07+)
For experienced developers ready for async and complex workflows:
7. **demo_07**: Async command orchestration (when ready for asyncio)
8. **demo_08**: Custom editor configuration
9+. **More complex patterns** (file browser, DataTable integration, etc.)

## Tips for Learning

1. **Read the docstring** - Each demo has a clear explanation of what it demonstrates
2. **Look at the comments** - Inline comments explain key concepts
3. **Try modifications** - Experiment by changing the code and seeing what breaks
4. **Run step by step** - Follow the progression in order; each demo builds on previous ones
5. **Check the README** - The main [README.md](../README.md) has comprehensive API documentation
6. **Compare examples** - Look at similar code in different demos to understand patterns

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

### For Beginners (Completed Demos 01-03)
1. Run demo_04 to see advanced icon patterns in action
2. Run demo_06 to understand how commands work
3. Run demo_05 to learn state management
4. Pick your favorite intermediate demo and modify it

### For Intermediate Learners (Completed Demos 04-06)
1. Choose which patterns matter most to your use case
2. Try modifying demos to combine features (e.g., state management + icons)
3. Refer to the main [README.md](../README.md) for full API documentation
4. Look at the source code in `src/textual_filelink/` for implementation details
5. Consider whether you're ready for async patterns in demo_07

### For Advanced Users
1. Build your own TUI application using patterns from these demos
2. Contribute improvements or new demos back to the project
3. Explore the Textual framework for more advanced patterns
4. Check the test suite in `tests/` for more examples

## Contributing

Found a bug in a demo? Want to suggest improvements? Please open an issue or pull request on GitHub!

## Resources

- **Main README:** [textual-filelink](../README.md)
- **Textual Documentation:** https://textual.textualize.io/
- **Source Code:** [src/textual_filelink/](../src/textual_filelink/)
- **Tests:** [tests/](../tests/)
