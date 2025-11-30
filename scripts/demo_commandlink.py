"""
Example app demonstrating CommandLink functionality.

This shows a simple command orchestrator with multiple commands
that can be run, stopped, and monitored.
"""

from pathlib import Path
import asyncio
from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button
from textual_filelink import CommandLink


class CommandOrchestratorApp(App):
    """Example app showing CommandLink for command orchestration."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    Vertical {
        width: 100;
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
    
    .controls {
        width: 100%;
        height: auto;
        margin: 1 0;
    }
    
    Button {
        margin: 0 1 0 0;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.running_commands = set()
        self.command_tasks = {}
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical():
            yield Static("🎯 Command Orchestrator", classes="title")
            
            # Example commands
            yield CommandLink(
                "Tests",
                output_path=None,
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            
            yield CommandLink(
                "Build",
                output_path=None,
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                initial_toggle=True,
                toggle_tooltip="Include in batch run",
            )
            
            yield CommandLink(
                "Lint",
                output_path=None,
                initial_status_icon="❓",
                initial_status_tooltip="Not run",
                toggle_tooltip="Include in batch run",
            )
            
            yield CommandLink(
                "Deploy",
                output_path=None,
                initial_status_icon="⚠️",
                initial_status_tooltip="Not configured",
                toggle_tooltip="Include in batch run",
            )
            
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
        
        # Update to running state
        link.set_status(running=True, tooltip=f"Running {event.name}...")
        self.running_commands.add(event.name)
        
        # Simulate command execution
        task = asyncio.create_task(self._simulate_command(event.name))
        self.command_tasks[event.name] = task
    
    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        """Handle stop button clicks - stop the command."""
        self.notify(f"⚠ Stopping {event.name}...", severity="warning")
        link = self.query_one(f"#{event.name}", CommandLink)
        
        # Cancel the task if it exists
        if event.name in self.command_tasks:
            self.command_tasks[event.name].cancel()
            del self.command_tasks[event.name]
        
        # Update to stopped state
        link.set_status(icon="⚠", running=False, tooltip="Stopped by user")
        self.running_commands.discard(event.name)
    
    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        """Handle settings icon clicks."""
        self.notify(f"⚙ Opening settings for {event.name}...")
        # In a real app, you'd open a modal or settings panel here
    
    def on_toggleable_file_link_toggled(self, event):
        """Handle toggle changes."""
        state = "selected" if event.is_toggled else "deselected"
        self.notify(f"{'☑' if event.is_toggled else '☐'} {event.path.name} {state}")
    
    def on_toggleable_file_link_removed(self, event):
        """Handle remove button clicks."""
        self.notify(f"🗑️ Removed {event.path.name}", severity="warning")
        
        # Cancel task if running
        name = event.path.name
        if name in self.command_tasks:
            self.command_tasks[name].cancel()
            del self.command_tasks[name]
        self.running_commands.discard(name)
        
        # Remove the widget
        for child in self.query(CommandLink):
            if child.name == name:
                child.remove()
    
    async def _simulate_command(self, name: str):
        """Simulate running a command with random success/failure."""
        try:
            # Simulate work
            duration = 3.0 if name != "Deploy" else 5.0
            await asyncio.sleep(duration)
            
            link = self.query_one(f"#{name}", CommandLink)
            
            # Simulate success/failure
            import random
            success = random.random() > 0.3  # 70% success rate
            
            if success:
                # Success
                output_path = Path(f"{name.lower()}_output.log")
                link.set_status(icon="✅", running=False, tooltip=f"Completed in {duration}s")
                link.set_output_path(output_path, tooltip="Click to view output")
                self.notify(f"✅ {name} completed successfully!", severity="information")
            else:
                # Failure
                output_path = Path(f"{name.lower()}_error.log")
                link.set_status(icon="❌", running=False, tooltip="Failed with errors")
                link.set_output_path(output_path, tooltip="Click to view errors")
                self.notify(f"❌ {name} failed!", severity="error")
            
            self.running_commands.discard(name)
            
        except asyncio.CancelledError:
            # Command was stopped
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
            if name in self.command_tasks:
                self.command_tasks[name].cancel()
                del self.command_tasks[name]
            
            try:
                link = self.query_one(f"#{name}", CommandLink)
                link.set_status(icon="⚠", running=False, tooltip="Stopped by user")
            except:
                pass
        
        self.running_commands.clear()
    
    def _reset_all(self):
        """Reset all commands to initial state."""
        # Stop all running commands first
        self._stop_all()
        
        # Reset all command states
        for link in self.query(CommandLink):
            link.set_status(icon="❓", running=False, tooltip="Not run")
            link.set_output_path(None)
            link.set_toggle(False, tooltip="Include in batch run")
        
        self.notify("🔄 Reset all commands")


if __name__ == "__main__":
    app = CommandOrchestratorApp()
    app.run()