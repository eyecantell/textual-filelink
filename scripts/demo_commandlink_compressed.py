"""
Compressed CommandLink demo - shows CommandLinks on single lines without descriptions.

This is a minimal version of demo_commandlink.py that displays all commands
in a compact format, useful for dashboards or space-constrained UIs.
"""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import CommandLink


class CompressedCommandApp(App):
    """Compact command orchestrator with single-line CommandLinks."""

    CSS = """
    Screen {
        align: center middle;
    }

    Vertical {
        width: 50;
        height: auto;
        border: solid green;
        padding: 1;
    }

    .title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    CommandLink {
        height: 1;
        margin: 0;
        padding: 0;
    }

    /* Remove focus border to keep single-line layout */
    CommandLink:focus {
        border: none;
        background: $accent 30%;
    }
    """

    def __init__(self):
        super().__init__()
        self.running_commands: set[str] = set()
        self.command_tasks: dict[str, asyncio.Task] = {}

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical():
            yield Static("Commands", classes="title")

            yield CommandLink(
                "Test",
                output_path=Path("test_output.log"),
                initial_status_icon="🧪",
                initial_status_tooltip="Run pytest",
                toggle_tooltip="Include in batch (t)",
                settings_tooltip="Test settings (s)",
                remove_tooltip="Remove command (x)",
                link_tooltip="Run pytest suite",
            )
            yield CommandLink(
                "Build",
                output_path=Path("build_output.log"),
                initial_status_icon="🔨",
                initial_status_tooltip="Build project",
                initial_toggle=True,
                toggle_tooltip="Include in batch (t)",
                settings_tooltip="Build settings (s)",
                remove_tooltip="Remove command (x)",
                link_tooltip="Build the project",
            )
            yield CommandLink(
                "Lint",
                output_path=Path("lint_output.log"),
                initial_status_icon="✨",
                initial_status_tooltip="Check code style",
                toggle_tooltip="Include in batch (t)",
                settings_tooltip="Lint settings (s)",
                remove_tooltip="Remove command (x)",
                link_tooltip="Check code style",
            )
            yield CommandLink(
                "Deploy",
                output_path=Path("deploy_output.log"),
                initial_status_icon="🚀",
                initial_status_tooltip="Deploy to production",
                toggle_tooltip="Include in batch (t)",
                settings_tooltip="Deploy settings (s)",
                remove_tooltip="Remove command (x)",
                link_tooltip="Deploy to production",
            )

        yield Footer()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        """Start the command."""
        self.notify(f"Starting {event.name}...")
        sanitized_id = CommandLink.sanitize_id(event.name)
        link = self.query_one(f"#{sanitized_id}", CommandLink)
        link.set_status(running=True, tooltip=f"Running {event.name}...")
        self.running_commands.add(event.name)

        task = asyncio.create_task(self._run_command(event.name))
        self.command_tasks[event.name] = task

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        """Stop the command."""
        self.notify(f"Stopping {event.name}...", severity="warning")
        sanitized_id = CommandLink.sanitize_id(event.name)
        link = self.query_one(f"#{sanitized_id}", CommandLink)

        if event.name in self.command_tasks:
            self.command_tasks[event.name].cancel()
            del self.command_tasks[event.name]

        link.set_status(icon="⚠", running=False, tooltip="Stopped")
        self.running_commands.discard(event.name)

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        """Open settings for the command."""
        self.notify(f"Settings for {event.name}")

    def on_toggleable_file_link_removed(self, event):
        """Remove the command."""
        command_name = event.path.name
        sanitized_id = CommandLink.sanitize_id(command_name)

        try:
            link = self.query_one(f"#{sanitized_id}", CommandLink)
            if command_name in self.command_tasks:
                self.command_tasks[command_name].cancel()
                del self.command_tasks[command_name]
            self.running_commands.discard(command_name)
            link.remove()
            self.notify(f"Removed {command_name}", severity="warning")
        except Exception:
            pass

    async def _run_command(self, name: str):
        """Simulate command execution."""
        try:
            await asyncio.sleep(2.0)

            sanitized_id = CommandLink.sanitize_id(name)
            link = self.query_one(f"#{sanitized_id}", CommandLink)

            import random
            success = random.random() > 0.3

            if success:
                link.set_status(icon="✅", running=False, tooltip="Success")
                self.notify(f"{name} completed!", severity="information")
            else:
                link.set_status(icon="❌", running=False, tooltip="Failed")
                self.notify(f"{name} failed!", severity="error")

            self.running_commands.discard(name)

        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    app = CompressedCommandApp()
    app.run()
