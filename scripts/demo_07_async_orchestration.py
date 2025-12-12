"""Demo 7: Async Command Orchestration - Simplified Async Patterns

This demo teaches how to run commands asynchronously with proper async/await patterns.

Demonstrates:
- asyncio.create_task() for creating background tasks
- Proper CancelledError handling and cleanup
- Timer-based elapsed time tracking
- Batch operations on selected commands
- Simple output file generation
- Task cancellation and graceful shutdown

Real-world use cases:
- Running multiple long-running commands without blocking UI
- Batch processing with progress tracking
- Command orchestration (pipelines, workflows)
- Background data processing or uploads/downloads
- Any TUI application that needs responsive UI during I/O

Key patterns:
- asyncio.create_task(coro) for background execution
- try/except asyncio.CancelledError for cleanup
- Timer-based progress updates (set_interval)
- Task dictionary for tracking multiple operations
- Elapsed time calculation and display

Prerequisites:
- Understand demo_06 (CommandLink basics)
- Basic understanding of async/await and asyncio
- Familiar with Python's time module

Notes:
- This is a SIMPLIFIED version focused on teaching async patterns
- See demo_commandlink.py for a full-featured orchestrator
- Target: ~250 lines (vs 484 in full version)
- Comments explain asyncio.create_task vs Textual's run_worker
"""

import asyncio
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
import time

from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import CommandLink


@dataclass
class CommandState:
    """Track state for a single command."""

    name: str
    status: str = "pending"  # pending, running, success, failed, stopped
    start_time: float | None = None


class AsyncCommandApp(App):
    """Demonstrate async command orchestration with Textual.

    This app shows how to:
    1. Create async tasks for background work
    2. Update UI while tasks run (non-blocking)
    3. Cancel tasks on user request
    4. Track elapsed time with timers
    5. Generate output files from completed commands
    """

    TITLE = "Demo 7: Async Command Orchestration - Simplified"
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
        border: solid green;
    }

    .description {
        width: 100%;
        color: $text-muted;
        margin: 1 0;
        height: auto;
    }

    CommandLink {
        width: 35;
        margin: 0 0 1 0;
    }

    .command-description {
        width: auto;
        color: $text-muted;
        margin: 0 0 1 3;
        height: auto;
    }

    .controls {
        width: 100%;
        height: auto;
        margin: 2 0 0 0;
        layout: horizontal;
    }

    Button {
        margin: 0 1 0 0;
    }
    """

    def __init__(self):
        super().__init__()
        # Track running async tasks by command name
        self.tasks: dict[str, asyncio.Task] = {}

        # Track command state (pending/running/success/failed)
        self.states: dict[str, CommandState] = {}

        # Track elapsed time timers (0.5s updates)
        self.timers: dict[str, object] = {}

        # Track start times for elapsed time calculation
        self.start_times: dict[str, float] = {}

    def compose(self) -> ComposeResult:
        """Create UI with 3 example commands and control buttons."""
        yield Header()

        with ScrollableContainer(id="content"):
            yield Static("⚙️ Async Command Orchestration", classes="title")

            yield Static(
                "Click play to run commands asynchronously. UI stays responsive while tasks run.",
                classes="description",
            )

            # Command 1: Fetch Data
            yield CommandLink(
                "Fetch Data",
                output_path=Path("scripts/fetch_output.md"),
                initial_status_icon="📥",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            yield Static("Simulates downloading data (3 seconds)", classes="command-description")

            # Command 2: Process Files
            yield CommandLink(
                "Process Files",
                output_path=Path("scripts/process_output.md"),
                initial_status_icon="⚙️",
                initial_status_tooltip="Not run",
                initial_toggle=True,
                toggle_tooltip="Include in batch run",
            )
            yield Static("Simulates processing data (5 seconds)", classes="command-description")

            # Command 3: Generate Report
            yield CommandLink(
                "Generate Report",
                output_path=Path("scripts/report_output.md"),
                initial_status_icon="📊",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            yield Static("Simulates report generation (4 seconds)", classes="command-description")

            # Control buttons
            with Horizontal(classes="controls"):
                yield Button("Run Selected", id="run-selected", variant="primary")
                yield Button("Stop All", id="stop-all", variant="error")
                yield Button("Reset All", id="reset-all")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize command states."""
        # Create initial state for each command
        for name in ["Fetch Data", "Process Files", "Generate Report"]:
            self.states[name] = CommandState(name=name)

    # ==== Event Handlers ====

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked) -> None:
        """Handle play button click - start async task.

        This is the key pattern:
        1. Create an asyncio task (non-blocking)
        2. Store it in self.tasks for later cancellation
        3. Start timer for elapsed time updates
        4. Update UI to show running state
        """
        self.notify(f"▶ Starting {event.name}...")

        # Map command name to duration for simulation
        durations = {
            "Fetch Data": 3.0,
            "Process Files": 5.0,
            "Generate Report": 4.0,
        }
        duration = durations.get(event.name, 3.0)

        # Get the CommandLink widget
        sanitized_id = CommandLink.sanitize_id(event.name)
        link = self.query_one(f"#{sanitized_id}", CommandLink)

        # Store start time for elapsed time calculation
        self.start_times[event.name] = time.time()

        # Update UI to running state
        link.set_status(running=True, tooltip=f"Running {event.name}...")

        # KEY PATTERN: Create async task
        # asyncio.create_task() returns immediately
        # The task runs in the background without blocking the UI
        # This is different from await, which waits for completion
        task = asyncio.create_task(self._run_command(event.name, duration))
        self.tasks[event.name] = task

        # Start timer for elapsed time updates (0.5s intervals)
        self.timers[event.name] = self.set_interval(
            0.5, lambda name=event.name: self._update_elapsed_time(name)
        )

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked) -> None:
        """Handle stop button click - cancel async task.

        Shows proper cleanup:
        1. Cancel the task (triggers CancelledError)
        2. Stop the elapsed time timer
        3. Update UI to show stopped state
        """
        self.notify(f"⚠ Stopping {event.name}...", severity="warning")

        # Stop the elapsed time timer
        if event.name in self.timers:
            self.timers[event.name].stop()
            del self.timers[event.name]

        # KEY PATTERN: Cancel the task
        # This sends a CancelledError to the async function
        # The function catches it and cleans up
        if event.name in self.tasks:
            self.tasks[event.name].cancel()
            del self.tasks[event.name]

        # Get the CommandLink widget and update UI
        sanitized_id = CommandLink.sanitize_id(event.name)
        link = self.query_one(f"#{sanitized_id}", CommandLink)
        link.set_status(icon="⏸️", running=False, tooltip="Stopped by user")

        # Clean up state
        self.start_times.pop(event.name, None)
        if event.name in self.states:
            self.states[event.name].status = "stopped"

    def on_toggleable_file_link_removed(self, event) -> None:
        """Handle remove button clicks.

        When user clicks the red X button:
        1. Stop any running timer for elapsed time
        2. Cancel the async task if running
        3. Clean up state tracking
        4. Remove the widget from UI
        5. Remove the description Static below it
        """
        # Extract command name from event
        # For CommandLink, event.path is Path(command_name)
        command_name = event.path.name

        # Get the CommandLink widget using sanitized ID
        try:
            sanitized_id = CommandLink.sanitize_id(command_name)
            link = self.query_one(f"#{sanitized_id}", CommandLink)
        except Exception:
            # Widget not found, already removed
            return

        # Stop elapsed time timer if running
        if link.name in self.timers:
            self.timers[link.name].stop()
            del self.timers[link.name]

        # Cancel running async task if present
        if link.name in self.tasks:
            self.tasks[link.name].cancel()
            del self.tasks[link.name]

        # Clean up state tracking
        self.start_times.pop(link.name, None)
        if link.name in self.states:
            del self.states[link.name]

        # Notify user
        self.notify(f"🗑️ Removed {link.name}", severity="warning")

        # Remove widget and its description Static from UI
        try:
            parent = link.parent
            if parent:
                children = list(parent.children)
                link_index = children.index(link)

                # Remove the CommandLink
                link.remove()

                # Remove description Static immediately after if present
                if link_index + 1 < len(children):
                    next_widget = children[link_index + 1]
                    if isinstance(next_widget, Static) and "command-description" in next_widget.classes:
                        next_widget.remove()
        except Exception:
            # Fallback: just remove the link
            link.remove()

    # ==== Async Command Execution ====

    async def _run_command(self, name: str, duration: float) -> None:
        """Execute a command asynchronously.

        This is where the actual async work happens. The key pattern:
        1. Do async work (asyncio.sleep simulates real I/O)
        2. Catch CancelledError if user stops the command
        3. Update UI on completion
        4. Generate output file
        """
        try:
            # Simulate async work (in real app, this would be actual I/O)
            # asyncio.sleep is async and allows other tasks to run
            await asyncio.sleep(duration)

            # Stop elapsed time timer
            if name in self.timers:
                self.timers[name].stop()
                del self.timers[name]

            # Get CommandLink widget
            sanitized_id = CommandLink.sanitize_id(name)
            link = self.query_one(f"#{sanitized_id}", CommandLink)

            # For this demo, all commands succeed (70% success in real app)
            # Generate output file
            output_file = self._generate_output_file(name, success=True, duration=duration)

            # Update UI with success
            link.set_status(icon="✅", running=False, tooltip=f"✅ Completed in {duration:.0f}s")
            link.set_output_path(output_file, tooltip="Click to view output")

            # Update state
            if name in self.states:
                self.states[name].status = "success"

            self.notify(f"✅ {name} completed!", severity="information")

            # Clean up task tracking
            self.tasks.pop(name, None)

        except asyncio.CancelledError:
            # KEY PATTERN: Proper CancelledError handling
            # This is raised when task.cancel() is called
            # Clean up any resources here
            if name in self.timers:
                self.timers[name].stop()
                del self.timers[name]

            # Update state
            if name in self.states:
                self.states[name].status = "stopped"

            # Clean up task tracking
            self.tasks.pop(name, None)

            # Don't notify - user already stopped it

    def _update_elapsed_time(self, name: str) -> None:
        """Update elapsed time display in tooltip.

        Called every 0.5s by the timer to show progress.
        """
        if name not in self.start_times:
            return

        elapsed = int(time.time() - self.start_times[name])
        try:
            sanitized_id = CommandLink.sanitize_id(name)
            link = self.query_one(f"#{sanitized_id}", CommandLink)
            link.set_status(tooltip=f"Running {name}... ({elapsed}s)")
        except Exception:
            # Widget might have been removed, stop trying
            pass

    def _generate_output_file(self, name: str, success: bool, duration: float) -> Path:
        """Generate simple output file for completed command.

        In a real app, this would contain actual command output.
        For demo purposes, we generate simple markdown.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        status = "✅ Success" if success else "❌ Failed"

        content = f"""# {name} Output

**Status:** {status}
**Duration:** {duration:.1f}s
**Timestamp:** {timestamp}

## Summary
Simulated command output for demonstration purposes.

## Details
- Command started successfully
- Processing completed normally
- No errors encountered

## Result
{status} - Command executed as expected.
"""

        # Map command to output filename
        output_map = {
            "Fetch Data": "fetch_output.md",
            "Process Files": "process_output.md",
            "Generate Report": "report_output.md",
        }
        filename = output_map.get(name, f"{name.lower()}_output.md")
        output_path = Path("scripts") / filename

        output_path.write_text(content)
        return output_path

    # ==== Batch Operations ====

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "run-selected":
            self._run_selected()
        elif event.button.id == "stop-all":
            self._stop_all()
        elif event.button.id == "reset-all":
            self._reset_all()

    def _run_selected(self) -> None:
        """Run all selected (toggled) commands."""
        selected = []
        for link in self.query(CommandLink):
            if link.is_toggled and link.name not in self.tasks:
                selected.append(link.name)

        if not selected:
            self.notify("⚠ No commands selected", severity="warning")
            return

        self.notify(f"▶ Running {len(selected)} command(s)...")

        # Run each selected command
        for name in selected:
            link = self.query_one(f"#{CommandLink.sanitize_id(name)}", CommandLink)
            link.set_status(running=True, tooltip=f"Running {name}...")
            # Trigger play clicked event for each
            link.post_message(
                CommandLink.PlayClicked(
                    path=link._output_path,
                    name=name,
                    output_path=link._output_path,
                    is_toggled=link._is_toggled,
                )
            )

    def _stop_all(self) -> None:
        """Stop all running commands."""
        if not self.tasks:
            self.notify("ℹ No commands running", severity="information")
            return

        count = len(self.tasks)
        self.notify(f"⚠ Stopping {count} command(s)...", severity="warning")

        for name in list(self.tasks.keys()):
            # Trigger stop clicked event
            self.post_message(
                CommandLink.StopClicked(
                    path=None,
                    name=name,
                    output_path=None,
                    is_toggled=False,
                )
            )

    def _reset_all(self) -> None:
        """Reset all commands to initial state."""
        # Stop all first
        if self.tasks:
            self._stop_all()

        # Reset all command states
        for link in self.query(CommandLink):
            link.set_status(icon="❓", running=False, tooltip="Not run")
            link.set_output_path(None)
            link.set_toggle(False, tooltip="Include in batch run")

        # Clear state tracking
        self.states = {name: CommandState(name=name) for name in self.states}

        self.notify("🔄 Reset all commands")


if __name__ == "__main__":
    app = AsyncCommandApp()
    app.run()
