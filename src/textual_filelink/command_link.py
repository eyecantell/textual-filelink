"""CommandLink widget - Command orchestration with status display (v0.4.0 refactor)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static

from .file_link import FileLink
from .utils import sanitize_id


class CommandLink(Horizontal, can_focus=True):
    """Command orchestration widget with status, play/stop, and optional settings.

    Flat architecture (no inheritance), builds own layout:
    [status/spinner] [▶️/⏹️] name [⚙️?]

    Toggle and remove controls are added by FileLinkList, not by CommandLink itself.

    Event Bubbling Policy
    ---------------------
    - Internal click handlers stop event propagation
    - Command messages (PlayClicked, StopClicked, etc.) bubble up by default
    - Parent containers can handle or stop these messages as needed

    Example
    -------
    >>> link = CommandLink(
    ...     "Tests",
    ...     initial_status_icon="❓",
    ...     initial_status_tooltip="Not run",
    ... )
    >>> link.set_status(running=True, tooltip="Running...")
    >>> link.set_status(icon="✅", running=False, tooltip="Passed")
    """

    DEFAULT_CSS = """
    CommandLink {
        width: auto;
        height: auto;
        padding: 0 1;
        border: none;
    }
    CommandLink > .status-icon {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    CommandLink > .play-stop-button {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $primary;
    }
    CommandLink > .play-stop-button:hover {
        text-style: bold;
        background: $boost;
    }
    CommandLink > .settings-icon {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $primary;
    }
    CommandLink > .settings-icon:hover {
        text-style: bold;
        background: $boost;
    }
    CommandLink:focus {
        background: $accent 20%;
        border: tall $accent;
    }
    """

    # Spinner frames for animation
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class PlayClicked(Message):
        """Posted when play button clicked.

        Attributes
        ----------
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.name = name
            self.output_path = output_path

    class StopClicked(Message):
        """Posted when stop button clicked.

        Attributes
        ----------
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.name = name
            self.output_path = output_path

    class SettingsClicked(Message):
        """Posted when settings icon clicked.

        Attributes
        ----------
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.name = name
            self.output_path = output_path

    class OutputClicked(Message):
        """Posted when command name clicked (opens output).

        Attributes
        ----------
        output_path : Path
            Output file path.
        """

        def __init__(self, output_path: Path) -> None:
            super().__init__()
            self.output_path = output_path

    def __init__(
        self,
        name: str,
        *,
        output_path: Path | str | None = None,
        command_builder: Callable | None = None,
        initial_status_icon: str = "❓",
        initial_status_tooltip: str | None = None,
        show_settings: bool = False,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        name : str
            Command name to display.
        output_path : Path | str | None
            Optional output file path. If set, clicking name opens the file.
        command_builder : Callable | None
            Optional command builder for opening output files.
        initial_status_icon : str
            Initial status icon (default: "❓").
        initial_status_tooltip : str | None
            Initial tooltip for status icon.
        show_settings : bool
            Whether to show settings icon (default: False).
        id : str | None
            Widget ID. If None, auto-generated from name via sanitize_id().
        classes : str | None
            CSS classes.
        """
        self._name = name
        self._output_path = Path(output_path).resolve() if output_path else None
        self._command_builder = command_builder
        self._show_settings = show_settings

        # Status state
        self._status_icon = initial_status_icon
        self._status_tooltip = initial_status_tooltip
        self._running = False

        # Spinner state
        self._spinner_frame_index = 0
        self._spinner_timer = None

        # Auto-generate ID if not provided
        widget_id = id or sanitize_id(name)

        # Set up keyboard bindings
        self.BINDINGS = [
            Binding("o", "open_output", "Open output", show=False),
            Binding("space", "play_stop", "Play/Stop", show=False),
            Binding("p", "play_stop", "Play/Stop", show=False),
        ]
        if show_settings:
            self.BINDINGS.append(Binding("s", "settings", "Settings", show=False))

        # Initialize container
        super().__init__(
            id=widget_id,
            classes=classes,
        )

        # Create child widgets
        self._status_widget = Static(self._status_icon, classes="status-icon")
        if self._status_tooltip:
            self._status_widget.tooltip = self._status_tooltip

        # Play/stop button
        self._play_stop_widget = Static("▶️", classes="play-stop-button")
        self._play_stop_widget.tooltip = "Run command (space/p)"
        self._play_stop_widget._is_play_button = True  # type: ignore

        # Name (FileLink if output_path, Static otherwise)
        if self._output_path:
            self._name_widget = FileLink(
                self._output_path,
                display_name=self._name,
                command_builder=self._command_builder,
                _embedded=True,
            )
        else:
            self._name_widget = Static(self._name)

        # Settings icon (optional)
        if self._show_settings:
            self._settings_widget = Static("⚙️", classes="settings-icon")
            self._settings_widget.tooltip = "Settings (s)"

    def compose(self):
        """Compose widget layout."""
        yield self._status_widget
        yield self._play_stop_widget
        yield self._name_widget
        if self._show_settings:
            yield self._settings_widget

    def on_click(self, event) -> None:
        """Handle clicks on child widgets."""
        event.stop()

        # Play/stop button
        if hasattr(event.widget, "_is_play_button"):
            if self._running:
                self.post_message(self.StopClicked(self._name, self._output_path))
            else:
                self.post_message(self.PlayClicked(self._name, self._output_path))

        # Settings icon
        elif event.widget == self._settings_widget if self._show_settings else False:
            self.post_message(self.SettingsClicked(self._name, self._output_path))

    # ------------------------------------------------------------------ #
    # Keyboard actions
    # ------------------------------------------------------------------ #
    def action_open_output(self) -> None:
        """Open output file (if set)."""
        if self._output_path and isinstance(self._name_widget, FileLink):
            self._name_widget.action_open_file()

    def action_play_stop(self) -> None:
        """Toggle play/stop."""
        if self._running:
            self.post_message(self.StopClicked(self._name, self._output_path))
        else:
            self.post_message(self.PlayClicked(self._name, self._output_path))

    def action_settings(self) -> None:
        """Open settings."""
        if self._show_settings:
            self.post_message(self.SettingsClicked(self._name, self._output_path))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def set_status(
        self,
        *,
        icon: str | None = None,
        running: bool | None = None,
        tooltip: str | None = None,
    ) -> None:
        """Update command status.

        Parameters
        ----------
        icon : str | None
            New status icon. If None, keeps current icon.
        running : bool | None
            Whether command is running. If True, starts spinner.
        tooltip : str | None
            New tooltip for status icon.

        Examples
        --------
        >>> link.set_status(running=True, tooltip="Running...")
        >>> link.set_status(icon="✅", running=False, tooltip="Passed")
        """
        if icon is not None:
            self._status_icon = icon

        if tooltip is not None:
            self._status_tooltip = tooltip
            self._status_widget.tooltip = tooltip

        if running is not None:
            was_running = self._running
            self._running = running

            # Update play/stop button
            if running:
                self._play_stop_widget.update("⏹️")
                self._play_stop_widget.tooltip = "Stop command (space/p)"
            else:
                self._play_stop_widget.update("▶️")
                self._play_stop_widget.tooltip = "Run command (space/p)"

            # Manage spinner
            if running and not was_running:
                # Start spinner
                self._spinner_frame_index = 0
                self._spinner_timer = self.set_interval(0.1, self._animate_spinner)
            elif not running and was_running:
                # Stop spinner, show final icon
                if self._spinner_timer:
                    self._spinner_timer.stop()
                    self._spinner_timer = None
                self._status_widget.update(self._status_icon)

    def set_output_path(self, output_path: Path | str | None) -> None:
        """Set or update the output file path.

        Parameters
        ----------
        output_path : Path | str | None
            New output path. If None, removes output path.
        """
        self._output_path = Path(output_path).resolve() if output_path else None

        # Update name widget if needed
        if self._output_path and not isinstance(self._name_widget, FileLink):
            # Replace Static with FileLink
            self._name_widget.remove()
            self._name_widget = FileLink(
                self._output_path,
                display_name=self._name,
                command_builder=self._command_builder,
                _embedded=True,
            )
            # Mount before settings widget if it exists, otherwise at end
            if self._show_settings:
                self.mount(self._name_widget, before=self._settings_widget)
            else:
                self.mount(self._name_widget)

    def _animate_spinner(self) -> None:
        """Animate the spinner (called by timer)."""
        if self._running:
            frame = self.SPINNER_FRAMES[self._spinner_frame_index]
            self._status_widget.update(frame)
            self._spinner_frame_index = (self._spinner_frame_index + 1) % len(self.SPINNER_FRAMES)

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def name(self) -> str:
        """Get command name."""
        return self._name

    @property
    def output_path(self) -> Path | None:
        """Get output file path."""
        return self._output_path

    @property
    def is_running(self) -> bool:
        """Check if command is currently running."""
        return self._running
