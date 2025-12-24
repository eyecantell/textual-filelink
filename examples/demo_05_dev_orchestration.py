"""Demo 5: Dev Command Orchestration - FileLinkList + CommandLink

This demo showcases combining FileLinkList with CommandLink to create a
dev command orchestration system for typical development workflows.

Key Features Demonstrated:
- FileLinkList containing CommandLink widgets
- Batch operations on selected commands (Run Selected, Stop Selected)
- Dev workflow patterns (Lint, Test, Format)
- Toggle selection for orchestrating multiple commands
- Status tracking across multiple commands
- Real-time statistics and monitoring
- Keyboard shortcuts for efficient workflow

This pattern is perfect for:
- Build tool orchestration (make, npm, cargo, etc.)
- Test runner suites (pytest, jest, vitest, etc.)
- Code quality pipelines (lint, format, type-check)
- Deployment workflows (build, test, deploy stages)

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate between widgets
- Space or P: Play/Stop the focused command
- T: Toggle selection of focused command
- X: Remove the focused command
- Enter or O: Open output file (when available)
- S: Open settings (when available)
- Q: Quit
"""

import asyncio
import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, Static

from textual_filelink import CommandLink, FileLinkList


class DevOrchestrationApp(App):
    """Dev command orchestration with FileLinkList and CommandLink."""

    TITLE = "Demo 5: Dev Command Orchestration"
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

    #subtitle {
        width: 100%;
        height: 2;
        content-align: center middle;
        color: $text-muted;
        background: $panel;
    }

    #main {
        width: 100%;
        height: 1fr;
        layout: horizontal;
    }

    #left-panel {
        width: 65%;
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }

    #right-panel {
        width: 35%;
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 1 0 0 0;
    }

    .description {
        width: 100%;
        color: $text-muted;
        margin: 0 0 1 0;
    }

    FileLinkList {
        height: auto;
        min-height: 10;
        max-height: 25;
        margin: 0 0 1 0;
        border: solid $primary;
    }

    #controls {
        width: 100%;
        height: auto;
        layout: vertical;
        border: solid $primary;
        padding: 1;
    }

    #controls Button {
        width: 100%;
        margin: 0 0 1 0;
    }

    #stats {
        width: 100%;
        height: auto;
        border: solid $accent;
        padding: 1;
        margin: 1 0;
    }

    #stats Label {
        width: 100%;
        margin: 0 0 1 0;
    }

    #workflow-status {
        width: 100%;
        height: auto;
        border: solid $success;
        padding: 1;
        margin: 1 0;
    }

    #workflow-status Label {
        width: 100%;
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        yield Static("🔧 Dev Command Orchestration", id="title")
        yield Static("FileLinkList + CommandLink = Powerful Workflow Control", id="subtitle")

        with Horizontal(id="main"):
            # Left panel: Command lists
            with Vertical(id="left-panel"):
                yield Static("Code Quality Pipeline", classes="section-title")
                yield Static(
                    "Select commands to run in batch. Toggle checkboxes to select/deselect.",
                    classes="description",
                )

                # Main command list
                yield FileLinkList(
                    show_toggles=True,
                    show_remove=True,
                    id="quality-commands",
                )

                yield Static("Build & Deploy Pipeline", classes="section-title")
                yield Static(
                    "Production-ready commands with output files and settings.",
                    classes="description",
                )

                # Build/deploy list
                yield FileLinkList(
                    show_toggles=True,
                    show_remove=False,  # Don't allow removal of critical commands
                    id="build-commands",
                )

                yield Static("Custom Commands", classes="section-title")
                yield Static(
                    "Add your own commands dynamically during runtime.",
                    classes="description",
                )

                # Custom command list
                yield FileLinkList(
                    show_toggles=True,
                    show_remove=True,
                    id="custom-commands",
                )

            # Right panel: Controls and stats
            with Vertical(id="right-panel"):
                yield Static("Batch Operations", classes="section-title")

                with Vertical(id="controls"):
                    yield Button("▶️ Run Selected", id="run-selected", variant="primary")
                    yield Button("⏹️ Stop Selected", id="stop-selected", variant="error")
                    yield Button("✅ Run All", id="run-all", variant="success")
                    yield Button("⏹️ Stop All", id="stop-all", variant="warning")
                    yield Static("", classes="description")  # Spacer
                    yield Button("☑️ Select All", id="select-all")
                    yield Button("☐ Deselect All", id="deselect-all")
                    yield Static("", classes="description")  # Spacer
                    yield Button("➕ Add Custom Command", id="add-custom")
                    yield Button("🗑️ Remove Selected", id="remove-selected", variant="error")
                    yield Static("", classes="description")  # Spacer
                    yield Button("🔄 Reset Demo", id="reset", variant="default")

                with Vertical(id="workflow-status"):
                    yield Static("Workflow Status", classes="section-title")
                    yield Label("⏸️ Idle", id="workflow-state")

                with Vertical(id="stats"):
                    yield Static("Statistics", classes="section-title")
                    yield Label("Total: 0 commands", id="stat-total")
                    yield Label("Selected: 0 commands", id="stat-selected")
                    yield Label("Running: 0 commands", id="stat-running")
                    yield Label("Success: 0", id="stat-success")
                    yield Label("Failed: 0", id="stat-failed")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize demo with commands."""
        self._running_count = 0
        self._success_count = 0
        self._failed_count = 0
        self._custom_counter = 1

        self.reset_demo()

    def reset_demo(self) -> None:
        """Reset demo to initial state."""
        # Clear all lists
        quality_list = self.query_one("#quality-commands", FileLinkList)
        build_list = self.query_one("#build-commands", FileLinkList)
        custom_list = self.query_one("#custom-commands", FileLinkList)

        quality_list.clear_items()
        build_list.clear_items()
        custom_list.clear_items()

        # Reset counters
        self._running_count = 0
        self._success_count = 0
        self._failed_count = 0

        # Populate quality commands
        quality_list.add_item(
            CommandLink(
                "Ruff Check",
                tooltip="Lint code with Ruff",
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to lint",
                id="cmd-ruff-check",
            ),
            toggled=True,  # Pre-selected for common workflows
        )

        quality_list.add_item(
            CommandLink(
                "Ruff Format",
                tooltip="Format code with Ruff",
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to format",
                id="cmd-ruff-format",
            ),
            toggled=True,  # Pre-selected
        )

        quality_list.add_item(
            CommandLink(
                "Pytest",
                tooltip="Run unit and integration tests",
                output_path=Path("sample_files/data.csv"),  # Mock coverage output
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to test",
                id="cmd-pytest",
            ),
            toggled=True,  # Pre-selected
        )

        quality_list.add_item(
            CommandLink(
                "MyPy",
                tooltip="Static type checking",
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to type-check",
                id="cmd-mypy",
            ),
            toggled=False,
        )

        # Populate build commands
        build_list.add_item(
            CommandLink(
                "PDM Build",
                tooltip="Build distribution packages",
                output_path=Path("sample_files/README.md"),  # Mock build output
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to build",
                id="cmd-build",
            ),
            toggled=False,
        )

        build_list.add_item(
            CommandLink(
                "Generate Docs",
                tooltip="Generate API documentation",
                output_path=Path("sample_files/notes.txt"),
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to generate docs",
                id="cmd-docs",
            ),
            toggled=False,
        )

        build_list.add_item(
            CommandLink(
                "Deploy to PyPI",
                tooltip="Publish package to PyPI",
                show_settings=True,
                initial_status_icon="●",
                initial_status_tooltip="Ready to deploy",
                id="cmd-deploy",
            ),
            toggled=False,
        )

        # Update stats
        self.update_stats()
        self.update_workflow_status("idle")

    def update_stats(self) -> None:
        """Update statistics display."""
        quality_list = self.query_one("#quality-commands", FileLinkList)
        build_list = self.query_one("#build-commands", FileLinkList)
        custom_list = self.query_one("#custom-commands", FileLinkList)

        total = len(quality_list) + len(build_list) + len(custom_list)
        selected = (
            len(quality_list.get_toggled_items())
            + len(build_list.get_toggled_items())
            + len(custom_list.get_toggled_items())
        )

        self.query_one("#stat-total", Label).update(f"Total: {total} commands")
        self.query_one("#stat-selected", Label).update(f"Selected: {selected} commands")
        self.query_one("#stat-running", Label).update(f"Running: {self._running_count} commands")
        self.query_one("#stat-success", Label).update(f"Success: {self._success_count}")
        self.query_one("#stat-failed", Label).update(f"Failed: {self._failed_count}")

    def update_workflow_status(self, status: str) -> None:
        """Update workflow status display."""
        status_map = {
            "idle": "⏸️ Idle",
            "running": "▶️ Running...",
            "success": "✅ All tasks completed successfully",
            "partial": "⚠️ Some tasks failed",
            "failed": "❌ Workflow failed",
        }
        self.query_one("#workflow-state", Label).update(status_map.get(status, status))

    async def run_command_simulation(self, command_id: str, duration: float = 2.0) -> bool:
        """Simulate running a command with random success/failure.

        Parameters
        ----------
        command_id : str
            ID of the CommandLink widget.
        duration : float
            Simulation duration in seconds.

        Returns
        -------
        bool
            True if command succeeded, False if it failed.
        """
        try:
            cmd = self.query_one(f"#{command_id}", CommandLink)
        except Exception:
            return False

        # Start running
        cmd.set_status(running=True)
        self._running_count += 1
        self.update_stats()

        # Wait for duration
        await asyncio.sleep(duration)

        # Random outcome (80% success for demos)
        success = random.random() < 0.8

        # Stop running with status
        if success:
            cmd.set_status(icon="✅", running=False, tooltip="Success!")
            self._success_count += 1
        else:
            cmd.set_status(icon="❌", running=False, tooltip="Failed")
            self._failed_count += 1

        self._running_count -= 1
        self.update_stats()

        return success

    async def run_selected_commands(self) -> None:
        """Run all selected commands in sequence."""
        quality_list = self.query_one("#quality-commands", FileLinkList)
        build_list = self.query_one("#build-commands", FileLinkList)
        custom_list = self.query_one("#custom-commands", FileLinkList)

        selected = quality_list.get_toggled_items() + build_list.get_toggled_items() + custom_list.get_toggled_items()

        if not selected:
            self.notify("⚠️ No commands selected", severity="warning", timeout=2)
            return

        self.update_workflow_status("running")
        self.notify(f"▶️ Running {len(selected)} selected commands...", timeout=2)

        results = []
        for cmd in selected:
            if isinstance(cmd, CommandLink):
                # Randomize duration for realism
                duration = random.uniform(1.5, 3.5)
                success = await self.run_command_simulation(cmd.id, duration)
                results.append(success)

        # Determine overall status
        if all(results):
            self.update_workflow_status("success")
            self.notify("✅ All selected commands succeeded!", timeout=3)
        elif any(results):
            self.update_workflow_status("partial")
            self.notify("⚠️ Some commands failed", severity="warning", timeout=3)
        else:
            self.update_workflow_status("failed")
            self.notify("❌ All commands failed", severity="error", timeout=3)

    def stop_selected_commands(self) -> None:
        """Stop all selected commands that are running."""
        quality_list = self.query_one("#quality-commands", FileLinkList)
        build_list = self.query_one("#build-commands", FileLinkList)
        custom_list = self.query_one("#custom-commands", FileLinkList)

        selected = quality_list.get_toggled_items() + build_list.get_toggled_items() + custom_list.get_toggled_items()

        stopped = 0
        for cmd in selected:
            if isinstance(cmd, CommandLink) and cmd.is_running:
                cmd.set_status(icon="⏹️", running=False, tooltip="Stopped by user")
                self._running_count -= 1
                stopped += 1

        self.update_stats()
        if stopped > 0:
            self.notify(f"⏹️ Stopped {stopped} commands", timeout=2)
            self.update_workflow_status("idle")
        else:
            self.notify("No running commands to stop", timeout=2)

    def on_file_link_list_item_toggled(self, event: FileLinkList.ItemToggled) -> None:
        """Handle item toggle events."""
        self.update_stats()

    def on_file_link_list_item_removed(self, event: FileLinkList.ItemRemoved) -> None:
        """Handle item removal events."""
        if isinstance(event.item, CommandLink):
            self.notify(f"🗑️ Removed: {event.item._command_name}", timeout=2)
        self.update_stats()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked) -> None:
        """Handle play button clicks."""
        self.notify(f"▶️ Starting: {event.name}", timeout=1)
        self.run_worker(self.run_command_simulation(event.widget.id))

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked) -> None:
        """Handle stop button clicks."""
        self.notify(f"⏹️ Stopping: {event.name}", timeout=1)
        event.widget.set_status(icon="⏹️", running=False, tooltip="Stopped")
        self._running_count -= 1
        self.update_stats()

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked) -> None:
        """Handle settings button clicks."""
        self.notify(f"⚙️ Settings for: {event.name}", timeout=2)

    def on_file_link_opened(self, event) -> None:
        """Handle output file opens (bubbled from embedded FileLink)."""
        if hasattr(event, "path"):
            self.notify(f"📂 Opening output: {event.path.name}", timeout=2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        quality_list = self.query_one("#quality-commands", FileLinkList)
        build_list = self.query_one("#build-commands", FileLinkList)
        custom_list = self.query_one("#custom-commands", FileLinkList)

        if event.button.id == "run-selected":
            self.run_worker(self.run_selected_commands())

        elif event.button.id == "stop-selected":
            self.stop_selected_commands()

        elif event.button.id == "run-all":
            # Select all first, then run
            quality_list.toggle_all(True)
            build_list.toggle_all(True)
            custom_list.toggle_all(True)
            self.update_stats()
            self.run_worker(self.run_selected_commands())

        elif event.button.id == "stop-all":
            # Stop all running commands
            for cmd in self.query(CommandLink):
                if cmd.is_running:
                    cmd.set_status(icon="⏹️", running=False, tooltip="Stopped")
                    self._running_count -= 1
            self.update_stats()
            self.update_workflow_status("idle")
            self.notify("⏹️ Stopped all commands", timeout=2)

        elif event.button.id == "select-all":
            quality_list.toggle_all(True)
            build_list.toggle_all(True)
            custom_list.toggle_all(True)
            self.update_stats()
            self.notify("☑️ All commands selected", timeout=1)

        elif event.button.id == "deselect-all":
            quality_list.toggle_all(False)
            build_list.toggle_all(False)
            custom_list.toggle_all(False)
            self.update_stats()
            self.notify("☐ All commands deselected", timeout=1)

        elif event.button.id == "remove-selected":
            selected_count = (
                len(quality_list.get_toggled_items())
                + len(build_list.get_toggled_items())
                + len(custom_list.get_toggled_items())
            )

            if selected_count == 0:
                self.notify("⚠️ No commands selected", severity="warning", timeout=2)
                return

            quality_list.remove_selected()
            build_list.remove_selected()
            custom_list.remove_selected()
            self.notify(f"🗑️ Removed {selected_count} commands", timeout=2)
            self.update_stats()

        elif event.button.id == "add-custom":
            # Add a custom command to the custom list
            custom_id = f"cmd-custom-{self._custom_counter}"
            custom_list.add_item(
                CommandLink(
                    f"Custom Task {self._custom_counter}",
                    show_settings=True,
                    initial_status_icon="●",
                    initial_status_tooltip="Custom command ready",
                    id=custom_id,
                ),
                toggled=False,
            )
            self._custom_counter += 1
            self.notify("➕ Added custom command", timeout=1)
            self.update_stats()

        elif event.button.id == "reset":
            self.reset_demo()
            self.notify("🔄 Demo reset to initial state", timeout=2)


if __name__ == "__main__":
    app = DevOrchestrationApp()
    app.run()
