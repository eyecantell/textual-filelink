"""
Example app demonstrating CommandLink functionality.

This shows a simple command orchestrator with multiple commands
that can be run, stopped, and monitored.
"""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static

from textual_filelink import CommandLink


class CommandOrchestratorApp(App):
    """Example app showing CommandLink for command orchestration."""

    CSS = """
    Screen {
        align: center middle;
    }

    Vertical {
        width: 60;
        height: auto;
        border: solid green;
        padding: 1;
    }

    .title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    CommandLink {
        width: 35;
        margin: 0 0 1 0;
    }

    .command-description {
        width: auto;
        color: $text-muted;
        margin: 0 0 1 3;
    }

    .controls {
        width: 100%;
        height: auto;
        margin: 2 0 0 0;
    }

    Button {
        margin: 0 1 0 0;
    }
    """

    def __init__(self):
        super().__init__()
        self.running_commands = set()
        self.command_tasks = {}
        self.command_start_times = {}
        self.command_elapsed_timers = {}

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("🎯 Command Orchestrator", classes="title")

            # Test command
            yield CommandLink(
                "Test",
                output_path=Path("scripts/tests_output.md"),
                initial_status_icon="🧪",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            yield Static("Run pytest test suite", classes="command-description")

            # Build command
            yield CommandLink(
                "Build",
                output_path=Path("scripts/build_output.md"),
                initial_status_icon="🔨",
                initial_status_tooltip="Not run",
                initial_toggle=True,
                toggle_tooltip="Include in batch run",
            )
            yield Static("Compile and bundle application", classes="command-description")

            # Lint command
            yield CommandLink(
                "Lint",
                output_path=Path("scripts/lint_output.md"),
                initial_status_icon="✨",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            yield Static("Check code style with ruff", classes="command-description")

            # Deploy command
            yield CommandLink(
                "Deploy",
                output_path=Path("scripts/deploy_output.md"),
                initial_status_icon="🚀",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            yield Static("Deploy to production server", classes="command-description")

            # Controls
            with Horizontal(classes="controls"):
                yield Button("Run Selected", id="run-selected", variant="primary")
                yield Button("Stop All", id="stop-all", variant="error")
                yield Button("Reset All", id="reset-all")

        yield Footer()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        """Handle play button clicks - start the command."""
        self.notify(f"▶ Starting {event.name}...")
        link = self.query_one(f"#{event.name}", CommandLink)

        # Track start time for elapsed time display
        import time

        self.command_start_times[event.name] = time.time()

        # Update to running state
        link.set_status(running=True, tooltip=f"Running {event.name}...")
        self.running_commands.add(event.name)

        # Start elapsed time timer
        self.command_elapsed_timers[event.name] = self.set_interval(
            0.5, lambda name=event.name: self._update_elapsed_time(name)
        )

        # Simulate command execution
        task = asyncio.create_task(self._simulate_command(event.name))
        self.command_tasks[event.name] = task

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        """Handle stop button clicks - stop the command."""
        self.notify(f"⚠ Stopping {event.name}...", severity="warning")
        link = self.query_one(f"#{event.name}", CommandLink)

        # Stop the elapsed time timer
        if event.name in self.command_elapsed_timers:
            self.command_elapsed_timers[event.name].stop()
            del self.command_elapsed_timers[event.name]

        # Cancel the task if it exists
        if event.name in self.command_tasks:
            self.command_tasks[event.name].cancel()
            del self.command_tasks[event.name]

        # Update to stopped state
        link.set_status(icon="⚠", running=False, tooltip="Stopped by user")
        self.running_commands.discard(event.name)
        self.command_start_times.pop(event.name, None)

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        """Handle settings icon clicks."""
        self.notify(f"⚙ Opening settings for {event.name}...")
        # In a real app, you'd open a modal or settings panel here

    def _update_elapsed_time(self, name: str) -> None:
        """Update the elapsed time display for a running command."""
        if name not in self.command_start_times:
            return

        import time

        elapsed = int(time.time() - self.command_start_times[name])
        try:
            link = self.query_one(f"#{name}", CommandLink)
            link.set_status(tooltip=f"Running {name}... ({elapsed}s)")
        except Exception:
            # Widget might have been removed
            pass

    def _generate_output_content(self, name: str, success: bool, duration: float) -> str:
        """Generate output content for a completed command."""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        status = "✅ Passed" if success else "❌ Failed"

        # Template generators for each command type
        templates = {
            "Test": lambda: f"""# Tests Output

**Status:** {status}
**Duration:** {duration}s
**Timestamp:** {timestamp}

## Summary
{"All tests passed successfully!" if success else "Some tests failed. Review details below."}

## Details
{"✓ test_file_link.py - All tests passed" if success else "✗ test_file_link.py - 2 failures"}
{"✓ test_toggleable_file_link.py - All tests passed" if success else "✓ test_toggleable_file_link.py - All tests passed"}
{"✓ test_command_link.py - All tests passed" if success else "✗ test_command_link.py - 1 failure"}
{"✓ test_integration.py - All tests passed" if success else "✓ test_integration.py - All tests passed"}

## Coverage
- Lines: {94 if success else 89}%
- Branches: {87 if success else 81}%
""",
            "Build": lambda: f"""# Build Output

**Status:** {status}
**Duration:** {duration}s
**Timestamp:** {timestamp}

## Summary
{"Build completed successfully." if success else "Build failed with compilation errors."}

## Details
{"✓ Compilation: Success" if success else "✗ Compilation: Failed"}
{"✓ Type checking: Passed" if success else "✓ Type checking: Passed"}
{"✓ Bundling: Complete" if success else "⊘ Bundling: Skipped"}

## Output
{"dist/textual-filelink-0.2.0-py3-none-any.whl" if success else "No artifacts generated"}
""",
            "Lint": lambda: f"""# Lint Output

**Status:** {status}
**Duration:** {duration}s
**Timestamp:** {timestamp}

## Summary
{"All code conforms to style standards." if success else "Style violations detected."}

## Issues Found
{0 if success else 3}

## Details
{"✓ No style issues" if success else "✗ 3 style violations found"}
{"✓ Complexity checks passed" if success else "⊘ Complexity checks skipped"}
""",
            "Deploy": lambda: f"""# Deploy Output

**Status:** {status}
**Duration:** {duration}s
**Timestamp:** {timestamp}

## Summary
{"Deployment successful - all instances healthy." if success else "Deployment failed - rolling back."}

## Instances
{"✓ 5/5 instances updated" if success else "✗ 2/5 instances failed"}

## Endpoint
{"https://api.example.com/v1" if success else "Service unavailable"}
""",
        }

        # Return template for command or default
        if name in templates:
            return templates[name]()
        return f"# {name} Output\n\nStatus: {status}\nDuration: {duration}s\n"

    def on_toggleable_file_link_toggled(self, event):
        """Handle toggle changes."""
        state = "selected" if event.is_toggled else "deselected"
        self.notify(f"{'☑' if event.is_toggled else '☐'} {event.path.name} {state}")

    def on_toggleable_file_link_removed(self, event):
        """Handle remove button clicks."""
        # event.control is the ToggleableFileLink/CommandLink that posted the event
        link = event.control

        if not isinstance(link, CommandLink):
            return

        # Cancel task if running
        if link.name in self.command_tasks:
            self.command_tasks[link.name].cancel()
            del self.command_tasks[link.name]
        self.running_commands.discard(link.name)
        self.command_start_times.pop(link.name, None)

        # Stop elapsed time timer
        if link.name in self.command_elapsed_timers:
            self.command_elapsed_timers[link.name].stop()
            del self.command_elapsed_timers[link.name]

        self.notify(f"🗑️ Removed {link.name} command", severity="warning")

        # Remove the widget
        link.remove()

    async def _simulate_command(self, name: str):
        """Simulate running a command with random success/failure."""
        try:
            # Simulate work
            duration = 3.0 if name != "Deploy" else 5.0
            await asyncio.sleep(duration)

            # Stop the elapsed time timer
            if name in self.command_elapsed_timers:
                self.command_elapsed_timers[name].stop()
                del self.command_elapsed_timers[name]

            link = self.query_one(f"#{name}", CommandLink)

            # Simulate success/failure
            import random

            success = random.random() > 0.3  # 70% success rate

            # Generate and write output to the markdown file
            output_content = self._generate_output_content(name, success, duration)
            # Map singular names to output filenames
            output_filenames = {
                "Test": "tests_output.md",
                "Build": "build_output.md",
                "Lint": "lint_output.md",
                "Deploy": "deploy_output.md",
            }
            output_file = Path(f"scripts/{output_filenames.get(name, name.lower() + '_output.md')}")
            output_file.write_text(output_content)

            if success:
                # Success
                link.set_status(icon="✅", running=False, tooltip=f"✅ Completed in {duration}s")
                link.set_output_path(output_file, tooltip="Click to view output")
                self.notify(f"✅ {name} completed successfully!", severity="information")
            else:
                # Failure
                link.set_status(icon="❌", running=False, tooltip=f"❌ Failed after {duration}s")
                link.set_output_path(output_file, tooltip="Click to view output")
                self.notify(f"❌ {name} failed!", severity="error")

            self.running_commands.discard(name)
            self.command_start_times.pop(name, None)

        except asyncio.CancelledError:
            # Command was stopped
            if name in self.command_elapsed_timers:
                self.command_elapsed_timers[name].stop()
                del self.command_elapsed_timers[name]
            pass

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        if event.button.id == "run-selected":
            self._run_selected()
        elif event.button.id == "stop-all":
            self._stop_all()
        elif event.button.id == "reset-all":
            self._reset_all()

    def _run_selected(self):
        """Run all selected (toggled) commands."""
        selected = []
        for link in self.query(CommandLink):
            if link.is_toggled and link.name not in self.running_commands:
                selected.append(link.name)

        if not selected:
            self.notify("⚠ No commands selected", severity="warning")
            return

        self.notify(f"▶ Running {len(selected)} selected command(s)...")

        for name in selected:
            link = self.query_one(f"#{name}", CommandLink)
            link.set_status(running=True, tooltip=f"Running {name}...")
            self.running_commands.add(name)

            task = asyncio.create_task(self._simulate_command(name))
            self.command_tasks[name] = task

    def _stop_all(self):
        """Stop all running commands."""
        if not self.running_commands:
            self.notify("ℹ No commands running", severity="information")
            return

        count = len(self.running_commands)
        self.notify(f"⚠ Stopping {count} command(s)...", severity="warning")

        for name in list(self.running_commands):
            # Stop the elapsed time timer
            if name in self.command_elapsed_timers:
                self.command_elapsed_timers[name].stop()
                del self.command_elapsed_timers[name]

            if name in self.command_tasks:
                self.command_tasks[name].cancel()
                del self.command_tasks[name]

            try:
                link = self.query_one(f"#{name}", CommandLink)
                link.set_status(icon="⚠", running=False, tooltip="Stopped by user")
            except Exception:
                pass

        self.running_commands.clear()
        self.command_start_times.clear()

    def _reset_all(self):
        """Reset all commands to initial state."""
        # Stop all running commands first
        self._stop_all()

        # Clear all timers and times
        for timer in self.command_elapsed_timers.values():
            timer.stop()
        self.command_elapsed_timers.clear()
        self.command_start_times.clear()

        # Reset all command states
        for link in self.query(CommandLink):
            link.set_status(icon="❓", running=False, tooltip="Not run")
            link.set_output_path(None)
            link.set_toggle(False, tooltip="Include in batch run")

        self.notify("🔄 Reset all commands")


if __name__ == "__main__":
    app = CommandOrchestratorApp()
    app.run()
