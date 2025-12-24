"""Demo 4: CommandLink - Command Orchestration with Status

This demo showcases CommandLink, a specialized widget for command execution
with status indicators, play/stop controls, and output file integration.

Key Features Demonstrated:
- Play/Stop buttons (▶️/⏹️)
- Status indicators with animated spinner
- Output file linking (click name when output exists)
- Settings icon (optional)
- Keyboard shortcuts (space/p for play/stop, enter/o for output, s for settings)
- Comprehensive tooltips showing available keyboard shortcuts
- Status tooltips for contextual information
- Status updates (running, success, failure, warning)
- Dynamic output path updates
- Command orchestration patterns

CommandLink combines status display, controls, and file linking in one widget,
perfect for build tools, test runners, deployment scripts, and async operations.

Keyboard Shortcuts:
- Tab/Shift+Tab: Navigate between widgets
- Space or P: Play/Stop the focused command
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

from textual_filelink import CommandLink


class CommandLinkDemo(App):
    """Comprehensive CommandLink demonstration."""

    TITLE = "Demo 4: CommandLink - Command Orchestration with Status"
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

    #main {
        width: 100%;
        height: 1fr;
        layout: horizontal;
    }

    #left-panel {
        width: 60%;
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }

    #right-panel {
        width: 40%;
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

    CommandLink {
        margin: 0 0 1 0;
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
    """

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()

        yield Static("⚙️ CommandLink - Command Orchestration", id="title")

        with Horizontal(id="main"):
            # Left panel: Command links
            with Vertical(id="left-panel"):
                yield Static("Section 1: Basic Command Links", classes="section-title")
                yield Static(
                    "Click ▶️ to run, ⏹️ to stop. Hover over elements for tooltips with keyboard shortcuts.",
                    classes="description",
                )

                yield CommandLink(
                    "Build Project",
                    initial_status_tooltip="Ready to build",
                    id="cmd-build",
                )

                yield CommandLink(
                    "Run Tests",
                    initial_status_tooltip="Ready to test",
                    id="cmd-test",
                )

                yield CommandLink(
                    "Deploy",
                    show_settings=True,
                    initial_status_tooltip="Ready to deploy",
                    id="cmd-deploy",
                )

                yield Static("Section 2: Commands with Output Files", classes="section-title")
                yield Static(
                    "When output_path is set, command name becomes clickable to open the file.",
                    classes="description",
                )

                yield CommandLink(
                    "Generate Report",
                    output_path=Path("sample_files/README.md"),
                    initial_status_tooltip="Report ready",
                    id="cmd-report",
                )

                yield CommandLink(
                    "Export Data",
                    output_path=Path("sample_files/data.csv"),
                    initial_status_tooltip="Data exported",
                    id="cmd-export",
                )

                yield Static("Section 3: Commands without Settings", classes="section-title")
                yield Static(
                    "Settings icon (⚙️) is optional via show_settings parameter.",
                    classes="description",
                )

                yield CommandLink(
                    "Simple Task",
                    show_settings=False,
                    initial_status_tooltip="Simple task ready",
                    id="cmd-simple",
                )

                yield Static("Section 4: Status Indicator Examples", classes="section-title")
                yield Static(
                    "Status icons show command state. Hover over status icons for tooltips.",
                    classes="description",
                )

                yield CommandLink(
                    "Status: Unknown",
                    initial_status_icon="❓",
                    initial_status_tooltip="Not yet run",
                    id="status-unknown",
                )

                yield CommandLink(
                    "Status: Success",
                    initial_status_icon="✅",
                    initial_status_tooltip="Tests passed",
                    id="status-success",
                )

                yield CommandLink(
                    "Status: Failed",
                    initial_status_icon="❌",
                    initial_status_tooltip="Build failed",
                    id="status-failed",
                )

                yield CommandLink(
                    "Status: Warning",
                    initial_status_icon="⚠️",
                    initial_status_tooltip="3 warnings found",
                    id="status-warning",
                )

            # Right panel: Controls and stats
            with Vertical(id="right-panel"):
                yield Static("Interactive Controls", classes="section-title")

                with Vertical(id="controls"):
                    yield Button("Run Build", id="run-build", variant="primary")
                    yield Button("Run Tests", id="run-test", variant="primary")
                    yield Button("Run Deploy", id="run-deploy", variant="primary")
                    yield Button("Run All", id="run-all", variant="success")
                    yield Button("Stop All", id="stop-all", variant="error")
                    yield Static("", classes="description")  # Spacer
                    yield Button("Update Statuses", id="update-statuses", variant="default")
                    yield Button("Simulate Success", id="sim-success", variant="success")
                    yield Button("Simulate Failure", id="sim-failure", variant="error")
                    yield Button("Reset Demo", id="reset", variant="default")

                with Vertical(id="stats"):
                    yield Static("Statistics", classes="section-title")
                    yield Label("Running: 0 commands", id="stat-running")
                    yield Label("Total Runs: 0", id="stat-total")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize demo state."""
        self._total_runs = 0
        self._running_count = 0
        self.update_stats()

    def update_stats(self) -> None:
        """Update statistics display."""
        self.query_one("#stat-running", Label).update(f"Running: {self._running_count} commands")
        self.query_one("#stat-total", Label).update(f"Total Runs: {self._total_runs}")

    async def run_command_simulation(self, command_id: str, duration: float = 2.0) -> None:
        """Simulate running a command with random success/failure.

        Parameters
        ----------
        command_id : str
            ID of the CommandLink widget.
        duration : float
            Simulation duration in seconds.
        """
        cmd = self.query_one(f"#{command_id}", CommandLink)

        # Start running
        cmd.set_status(running=True)
        self._running_count += 1
        self._total_runs += 1
        self.update_stats()

        # Wait for duration
        await asyncio.sleep(duration)

        # Random outcome (70% success, 30% failure)
        success = random.random() < 0.7

        # Stop running with status
        if success:
            cmd.set_status(icon="✅", running=False, tooltip="Success!")
        else:
            cmd.set_status(icon="❌", running=False, tooltip="Failed")

        self._running_count -= 1
        self.update_stats()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked) -> None:
        """Handle play button clicks."""
        self.notify(f"▶️ Starting: {event.name}", timeout=1)
        # Run simulation in background using the widget reference
        self.run_worker(self.run_command_simulation(event.widget.id))

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked) -> None:
        """Handle stop button clicks."""
        self.notify(f"⏹️ Stopping: {event.name}", timeout=1)
        # Update the widget directly using the widget reference
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
        if event.button.id == "run-build":
            cmd = self.query_one("#cmd-build", CommandLink)
            self.run_worker(self.run_command_simulation("cmd-build", 2.0))

        elif event.button.id == "run-test":
            cmd = self.query_one("#cmd-test", CommandLink)
            self.run_worker(self.run_command_simulation("cmd-test", 3.0))

        elif event.button.id == "run-deploy":
            cmd = self.query_one("#cmd-deploy", CommandLink)
            self.run_worker(self.run_command_simulation("cmd-deploy", 4.0))

        elif event.button.id == "run-all":
            self.run_worker(self.run_command_simulation("cmd-build", 2.0))
            self.run_worker(self.run_command_simulation("cmd-test", 3.0))
            self.run_worker(self.run_command_simulation("cmd-deploy", 4.0))
            self.notify("▶️ Running all commands...", timeout=2)

        elif event.button.id == "stop-all":
            # Stop all running commands
            for cmd_id in ["cmd-build", "cmd-test", "cmd-deploy", "cmd-report", "cmd-export", "cmd-simple"]:
                try:
                    cmd = self.query_one(f"#{cmd_id}", CommandLink)
                    if cmd.is_running:
                        cmd.set_status(icon="⏹️", running=False, tooltip="Stopped")
                        self._running_count -= 1
                except Exception:
                    pass
            self.update_stats()
            self.notify("⏹️ Stopped all commands", timeout=2)

        elif event.button.id == "update-statuses":
            # Cycle through different status icons
            statuses = [
                ("status-unknown", "❓", "Status: Unknown"),
                ("status-success", "✅", "Status: Success"),
                ("status-failed", "❌", "Status: Failed"),
                ("status-warning", "⚠️", "Status: Warning"),
            ]
            for cmd_id, icon, tooltip in statuses:
                cmd = self.query_one(f"#{cmd_id}", CommandLink)
                cmd.set_status(icon=icon, tooltip=tooltip)
            self.notify("📊 Updated all status indicators", timeout=2)

        elif event.button.id == "sim-success":
            # Set all commands to success state
            for cmd_id in ["cmd-build", "cmd-test", "cmd-deploy", "cmd-report", "cmd-export", "cmd-simple"]:
                try:
                    cmd = self.query_one(f"#{cmd_id}", CommandLink)
                    cmd.set_status(icon="✅", running=False, tooltip="Success!")
                except Exception:
                    pass
            self.notify("✅ All commands succeeded", timeout=2)

        elif event.button.id == "sim-failure":
            # Set all commands to failure state
            for cmd_id in ["cmd-build", "cmd-test", "cmd-deploy", "cmd-report", "cmd-export", "cmd-simple"]:
                try:
                    cmd = self.query_one(f"#{cmd_id}", CommandLink)
                    cmd.set_status(icon="❌", running=False, tooltip="Failed")
                except Exception:
                    pass
            self.notify("❌ All commands failed", timeout=2)

        elif event.button.id == "reset":
            # Reset all commands to initial state
            for cmd_id in ["cmd-build", "cmd-test", "cmd-deploy", "cmd-report", "cmd-export", "cmd-simple"]:
                try:
                    cmd = self.query_one(f"#{cmd_id}", CommandLink)
                    cmd.set_status(icon="●", running=False, tooltip="Ready")
                except Exception:
                    pass
            # Reset status examples
            statuses = [
                ("status-unknown", "❓", "Status: Unknown"),
                ("status-success", "✅", "Status: Success"),
                ("status-failed", "❌", "Status: Failed"),
                ("status-warning", "⚠️", "Status: Warning"),
            ]
            for cmd_id, icon, tooltip in statuses:
                cmd = self.query_one(f"#{cmd_id}", CommandLink)
                cmd.set_status(icon=icon, tooltip=tooltip)

            self._running_count = 0
            self._total_runs = 0
            self.update_stats()
            self.notify("🔄 Demo reset to initial state", timeout=2)


if __name__ == "__main__":
    app = CommandLinkDemo()
    app.run()
