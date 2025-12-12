"""Demo 4: Icons Advanced - Master the Icon System

This demo builds on demo_03 by showing more advanced icon patterns and interactions.

It demonstrates:
- Icon ordering with explicit indices
- Multiple icons at before and after positions
- Icon visibility toggling with controls
- Interactive icon workflows (processing, cascading states)
- Simulated async operations with timers
- Control buttons for batch operations

Real-world use cases:
- File validation workflows (locked → edit → save)
- Processing pipelines (pending → processing → done)
- Multi-status indicators (warnings, errors, priorities)
- File operations with multiple states

This is an intermediate demo. See demo_multiple_icons.py for more complex
patterns, and demo_05_state_management.py for state management approaches.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import ToggleableFileLink


class IconsAdvancedApp(App):
    """Demonstrate advanced icon usage in file links."""

    TITLE = "Demo 4: Icons Advanced - Master the Icon System"
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        layout: vertical;
    }

    #title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $boost;
    }

    #content {
        width: 100%;
        height: 1fr;
        padding: 1;
        overflow: auto;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 2 0 1 0;
    }

    .section-description {
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
        height: auto;
    }

    ToggleableFileLink {
        margin: 0 0 1 0;
    }

    .controls {
        width: 100%;
        height: auto;
        margin: 2 0 0 0;
    }

    Button {
        margin-right: 1;
    }
    """

    def __init__(self):
        super().__init__()
        # Track which icons are visible for batch operations
        self.warning_visible = False
        self.error_visible = False

    def compose(self) -> ComposeResult:
        """Create the UI with advanced icon examples."""
        yield Header()

        # Title
        yield Static(
            "🎨 Advanced Icon Features - Learn Icon Mastery",
            id="title",
        )

        with Vertical(id="content"):
            # Example 1: Icon Ordering
            yield Static("1️⃣ Icon Ordering with Indices", classes="section-title")
            yield Static(
                "Icons are displayed in order of their indices, not list order. "
                "This file has indices 3, 1, 2 but displays as 1, 2, 3.",
                classes="section-description",
            )
            yield ToggleableFileLink(
                Path("sample_files/example.py"),
                icons=[
                    {
                        "name": "third",
                        "icon": "3️⃣",
                        "index": 3,
                        "tooltip": "Third position",
                    },
                    {
                        "name": "first",
                        "icon": "1️⃣",
                        "index": 1,
                        "tooltip": "First position",
                    },
                    {
                        "name": "second",
                        "icon": "2️⃣",
                        "index": 2,
                        "tooltip": "Second position",
                    },
                ],
            )

            # Example 2: Before & After Positioning
            yield Static("2️⃣ Icons Before and After Filename", classes="section-title")
            yield Static(
                "Position icons on either side of the filename to organize metadata. "
                "Type and status before, size and sync after.",
                classes="section-description",
            )
            yield ToggleableFileLink(
                Path("sample_files/config.json"),
                icons=[
                    {
                        "name": "type",
                        "icon": "⚙️",
                        "position": "before",
                        "tooltip": "Configuration file",
                    },
                    {
                        "name": "status",
                        "icon": "✓",
                        "position": "before",
                        "tooltip": "Valid config",
                    },
                    {
                        "name": "size",
                        "icon": "📊",
                        "position": "after",
                        "tooltip": "File size indicator",
                    },
                    {
                        "name": "sync",
                        "icon": "☁️",
                        "position": "after",
                        "tooltip": "Cloud synced",
                    },
                ],
            )

            # Example 3: Visibility Toggling
            yield Static("3️⃣ Visibility Control with Buttons", classes="section-title")
            yield Static(
                "Icons can be hidden or shown dynamically. Use the buttons below "
                "to toggle warning and error visibility.",
                classes="section-description",
            )
            yield ToggleableFileLink(
                Path("sample_files/data.csv"),
                id="visibility-demo",
                icons=[
                    {
                        "name": "valid",
                        "icon": "✓",
                        "tooltip": "Data is valid",
                    },
                    {
                        "name": "warning",
                        "icon": "⚠️",
                        "visible": False,
                        "tooltip": "Contains warnings",
                    },
                    {
                        "name": "error",
                        "icon": "❌",
                        "visible": False,
                        "position": "after",
                        "tooltip": "Validation errors",
                    },
                ],
            )

            # Example 4: Processing States with Timers
            yield Static("4️⃣ Processing States - Click to Start", classes="section-title")
            yield Static(
                "Click the processing icon to simulate a 2-second operation. The result icon appears when complete.",
                classes="section-description",
            )
            yield ToggleableFileLink(
                Path("sample_files/notes.txt"),
                id="processing-demo",
                icons=[
                    {
                        "name": "process",
                        "icon": "⏳",
                        "clickable": True,
                        "tooltip": "Click to process",
                    },
                    {
                        "name": "result",
                        "icon": "⚪",
                        "visible": False,
                        "position": "after",
                        "tooltip": "Processing result",
                    },
                ],
            )

            # Example 5: Cascading Workflow
            yield Static("5️⃣ Cascading Icon Workflow", classes="section-title")
            yield Static(
                "Complex workflows with dependent icons: unlock → edit → save. "
                "Click each icon to progress through the workflow.",
                classes="section-description",
            )
            yield ToggleableFileLink(
                Path("sample_files/Makefile"),
                id="workflow-demo",
                icons=[
                    {
                        "name": "lock",
                        "icon": "🔒",
                        "clickable": True,
                        "tooltip": "Locked. Click to unlock.",
                    },
                    {
                        "name": "edit",
                        "icon": "📝",
                        "visible": False,
                        "clickable": True,
                        "tooltip": "Unlocked. Click to edit.",
                    },
                    {
                        "name": "save",
                        "icon": "💾",
                        "visible": False,
                        "position": "after",
                        "tooltip": "Edited. Click to save.",
                    },
                ],
            )

            # Control buttons
            with Horizontal(classes="controls"):
                yield Button("Show Warnings", id="show-warnings", variant="primary")
                yield Button("Hide Warnings", id="hide-warnings")
                yield Button("Reset All", id="reset-all")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle control button presses."""
        if event.button.id == "show-warnings":
            # Show hidden warning/error icons
            link = self.query_one("#visibility-demo", ToggleableFileLink)
            if not self.warning_visible:
                link.set_icon_visible("warning", True)
                self.warning_visible = True
                self.notify("⚠️ Warnings now visible", timeout=1.5)
            if not self.error_visible:
                link.set_icon_visible("error", True)
                self.error_visible = True

        elif event.button.id == "hide-warnings":
            # Hide warning/error icons
            link = self.query_one("#visibility-demo", ToggleableFileLink)
            if self.warning_visible:
                link.set_icon_visible("warning", False)
                self.warning_visible = False
            if self.error_visible:
                link.set_icon_visible("error", False)
                self.error_visible = False
            self.notify("⚠️ Warnings now hidden", timeout=1.5)

        elif event.button.id == "reset-all":
            # Reset all examples to initial state
            self._reset_all_examples()
            self.notify("🔄 All examples reset to initial state", timeout=1.5)

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle clickable icon interactions."""
        if event.path.name == "notes.txt":
            # Handle processing demo
            self._handle_processing_click(event)
        elif event.path.name == "Makefile":
            # Handle workflow demo (cascading icons)
            self._handle_workflow_click(event)

    def _handle_processing_click(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle processing icon clicks with timer simulation.

        Simulates a 2-second processing operation. When complete, shows the
        result icon with a success indicator.
        """
        link = self.query_one("#processing-demo", ToggleableFileLink)

        if event.icon_name == "process":
            # Start processing
            link.update_icon("process", icon="⌛", tooltip="Processing...")
            self.notify("⏳ Processing started...", timeout=1)

            # Simulate async work with timer (2 seconds)
            def complete_processing():
                """Callback when processing completes."""
                link.update_icon("process", icon="✓", tooltip="Complete!")
                link.set_icon_visible("result", True)
                link.update_icon("result", icon="🟢", tooltip="Success!")
                self.notify("✅ Processing complete!", timeout=2)

            self.set_timer(2.0, complete_processing)

    def _handle_workflow_click(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle cascading workflow icon clicks.

        Demonstrates a multi-step workflow:
        1. Click lock → unlocks and shows edit icon
        2. Click edit → hides edit, shows save icon
        3. Click save → marks as saved
        """
        link = self.query_one("#workflow-demo", ToggleableFileLink)

        if event.icon_name == "lock":
            # Unlock: show edit icon, hide lock
            link.set_icon_visible("lock", False)
            link.set_icon_visible("edit", True)
            self.notify("🔓 Unlocked - Edit is now available", timeout=1.5)

        elif event.icon_name == "edit":
            # Start editing: show save icon, hide edit
            link.update_icon("edit", icon="✏️", tooltip="Editing...")
            self.set_timer(
                1.0,
                lambda: self._complete_edit(link),
            )
            self.notify("✏️ Editing in progress...", timeout=1)

        elif event.icon_name == "save":
            # Save: complete the workflow
            link.update_icon("save", icon="✅", tooltip="Saved!")
            self.notify("💾 File saved successfully!", timeout=2)

    def _complete_edit(self, link: ToggleableFileLink) -> None:
        """Complete the edit step and show save icon."""
        link.set_icon_visible("edit", False)
        link.set_icon_visible("save", True)
        self.notify("✅ Ready to save", timeout=1.5)

    def _reset_all_examples(self) -> None:
        """Reset all demo examples to their initial state."""
        # Reset processing demo
        proc_link = self.query_one("#processing-demo", ToggleableFileLink)
        proc_link.update_icon("process", icon="⏳", tooltip="Click to process")
        proc_link.set_icon_visible("result", False)

        # Reset workflow demo
        workflow_link = self.query_one("#workflow-demo", ToggleableFileLink)
        workflow_link.set_icon_visible("lock", True)
        workflow_link.set_icon_visible("edit", False)
        workflow_link.set_icon_visible("save", False)
        workflow_link.update_icon("lock", icon="🔒", tooltip="Locked. Click to unlock.")
        workflow_link.update_icon("edit", icon="📝", tooltip="Unlocked. Click to edit.")
        workflow_link.update_icon("save", icon="💾", tooltip="Edited. Click to save.")

        # Reset visibility demo
        vis_link = self.query_one("#visibility-demo", ToggleableFileLink)
        self.warning_visible = False
        self.error_visible = False
        vis_link.set_icon_visible("warning", False)
        vis_link.set_icon_visible("error", False)


if __name__ == "__main__":
    app = IconsAdvancedApp()
    app.run()
