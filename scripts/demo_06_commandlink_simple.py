"""Demo 6: CommandLink Simple - Introduce CommandLink Basics

This is the simplest CommandLink example. It demonstrates:
- CommandLink widget basics (play/stop buttons)
- Simple status indicators
- Timer-based command simulation (synchronous, NO async)
- CommandLink events (PlayClicked, StopClicked, SettingsClicked)
- Output file path concept

This demo is intentionally simple to introduce CommandLink without overwhelming
complexity. Key simplifications:
- Synchronous operation (no async/await)
- No batch operations (no toggle controls)
- No output file generation (just simulate)
- No elapsed time tracking
- Just play/stop, status updates, notifications

CommandLink is a specialized widget for managing commands. When clicked, it emits
events that your app handles to run commands and update status. This demo shows
the fundamental patterns before more complex examples.

See demo_05_state_management.py for state patterns, and demo_07_commandlink_advanced.py
for async execution and batch operations.
"""

import random
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static

from textual_filelink import CommandLink


class CommandLinkSimpleApp(App):
    """Demonstrate basic CommandLink functionality."""

    TITLE = "Demo 6: CommandLink Simple - Introduction to Commands"
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

    .description {
        width: 100%;
        color: $text-muted;
        margin-bottom: 2;
        height: auto;
    }

    .command-section {
        width: 100%;
        margin-bottom: 2;
        height: auto;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    CommandLink {
        margin-bottom: 1;
    }

    .hint {
        width: 100%;
        color: $text-muted;
        margin: 1 0 0 0;
        height: auto;
    }
    """

    def __init__(self):
        super().__init__()
        # Track running timers so we can cancel them if user clicks stop
        self.command_timers = {}

    def compose(self) -> ComposeResult:
        """Create the UI with simple command examples."""
        yield Header()

        # Title
        yield Static(
            "⚙️ CommandLink Basics - Play, Stop, and Status",
            id="title",
        )

        with Vertical(id="content"):
            # Explanation
            yield Static(
                "CommandLink displays commands with play/stop buttons and status icons. "
                "Click the play button to simulate running a command. "
                "The status icon updates to show what's happening.",
                classes="description",
            )

            # Example 1: Simple command
            yield Static("Basic Command", classes="section-title")
            yield CommandLink(
                "Format Code",
                output_path=None,
                initial_status_icon="❓",
                initial_status_tooltip="Not run yet",
                show_toggle=False,
                show_settings=False,
                show_remove=False,
            )
            yield Static(
                "Simple command: click play → 2 second simulation → ✅ or ❌",
                classes="hint",
            )

            # Example 2: Command with output file
            yield Static("Command with Output File", classes="section-title")
            yield CommandLink(
                "Run Tests",
                output_path=Path("sample_files/example.py"),
                initial_status_icon="🧪",
                initial_status_tooltip="Tests not run",
                show_toggle=False,
                show_settings=False,
                show_remove=False,
            )
            yield Static(
                "Has output file (sample_files/example.py). Click the command name to open it.",
                classes="hint",
            )

            # Example 3: Command with settings
            yield Static("Command with Settings Button", classes="section-title")
            yield CommandLink(
                "Build Project",
                output_path=None,
                initial_status_icon="🔨",
                initial_status_tooltip="Not built",
                show_toggle=False,
                show_settings=True,  # This one has settings
                show_remove=False,
            )
            yield Static(
                "Click settings icon to show notification. "
                "Settings would configure command options in a real app.",
                classes="hint",
            )

        yield Footer()

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked) -> None:
        """Handle play button click - start simulated command.

        When the user clicks play, we:
        1. Update status to show running (either with spinner or icon)
        2. Start a timer for simulated work
        3. Show notification that command started
        """
        # Find the command link widget
        link = self.query_one(f"#{event.name}", CommandLink)

        # Update status to show running
        link.set_status(running=True, tooltip=f"Running {event.name}...")
        self.notify(f"▶️ Started: {event.name}", timeout=1.5)

        # Simulate async work with a timer (2 seconds for demo)
        # In a real app, you'd use asyncio or similar for actual async work
        timer = self.set_timer(2.0, lambda: self._complete_command(event.name))
        self.command_timers[event.name] = timer

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked) -> None:
        """Handle stop button click - cancel running command.

        When the user clicks stop, we:
        1. Cancel the running operation (in this case, the timer)
        2. Update status to show it was cancelled
        3. Show notification
        """
        # Find the command link widget
        link = self.query_one(f"#{event.name}", CommandLink)

        # Cancel the timer if it's running
        if event.name in self.command_timers:
            timer = self.command_timers.pop(event.name)
            timer.stop()

        # Update status to show cancelled
        link.set_status(icon="⏸️", running=False, tooltip="Cancelled")
        self.notify(f"⏹️ Stopped: {event.name}", severity="warning", timeout=1.5)

    def on_command_link_settings_clicked(
        self, event: CommandLink.SettingsClicked
    ) -> None:
        """Handle settings button click - show command configuration.

        In this simple demo, we just show a notification. In a real app,
        you might open a settings dialog or configuration menu.
        """
        self.notify(
            f"⚙️ Settings for {event.name} (not implemented in demo)",
            timeout=2,
        )

    def _complete_command(self, name: str) -> None:
        """Complete the command simulation.

        After 2 seconds of simulated work, we:
        1. Generate random success/failure (70% success for demo)
        2. Update status icon to show result
        3. Update running state to show it's done
        4. Show notification
        """
        link = self.query_one(f"#{name}", CommandLink)

        # Random success/failure for variety (70% success rate)
        success = random.random() > 0.3

        if success:
            # Command succeeded
            link.set_status(icon="✅", running=False, tooltip="Success!")
            self.notify(f"✅ {name} completed successfully!", timeout=2)
        else:
            # Command failed
            link.set_status(icon="❌", running=False, tooltip="Failed")
            self.notify(f"❌ {name} failed", severity="error", timeout=2)

        # Clean up timer reference
        if name in self.command_timers:
            del self.command_timers[name]


if __name__ == "__main__":
    app = CommandLinkSimpleApp()
    app.run()
