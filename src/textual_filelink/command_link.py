"""CommandLink widget - Command orchestration with status display (v0.4.0 refactor)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Static

from .file_link import FileLink
from .utils import format_keyboard_shortcuts, sanitize_id


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
    }
    CommandLink > .command-name {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    CommandLink > FileLink {
        width: auto;
        height: 1;
        padding: 0 1;
    }
    """

    # Spinner frames for animation
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class PlayClicked(Message):
        """Posted when play button clicked.

        Attributes
        ----------
        widget : CommandLink
            The CommandLink widget that was clicked.
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, widget: CommandLink, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.widget = widget
            self.name = name
            self.output_path = output_path

    class StopClicked(Message):
        """Posted when stop button clicked.

        Attributes
        ----------
        widget : CommandLink
            The CommandLink widget that was clicked.
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, widget: CommandLink, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.widget = widget
            self.name = name
            self.output_path = output_path

    class SettingsClicked(Message):
        """Posted when settings icon clicked.

        Attributes
        ----------
        widget : CommandLink
            The CommandLink widget that was clicked.
        name : str
            Command name.
        output_path : Path | None
            Output file path if set.
        """

        def __init__(self, widget: CommandLink, name: str, output_path: Path | None) -> None:
            super().__init__()
            self.widget = widget
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

    # Default keyboard shortcuts
    DEFAULT_OPEN_KEYS = ["enter", "o"]
    DEFAULT_PLAY_STOP_KEYS = ["space", "p"]
    DEFAULT_SETTINGS_KEYS = ["s"]

    def __init__(
        self,
        name: str,
        *,
        output_path: Path | str | None = None,
        command_builder: Callable | None = None,
        initial_status_icon: str = "❓",
        initial_status_tooltip: str | None = None,
        show_settings: bool = False,
        open_keys: list[str] | None = None,
        play_stop_keys: list[str] | None = None,
        settings_keys: list[str] | None = None,
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
        open_keys : list[str] | None
            Custom keyboard shortcuts for opening output. If None, uses DEFAULT_OPEN_KEYS.
        play_stop_keys : list[str] | None
            Custom keyboard shortcuts for play/stop. If None, uses DEFAULT_PLAY_STOP_KEYS.
        settings_keys : list[str] | None
            Custom keyboard shortcuts for settings. If None, uses DEFAULT_SETTINGS_KEYS.
        id : str | None
            Widget ID. If None, auto-generated from name via sanitize_id().
        classes : str | None
            CSS classes.
        """
        self._command_name = name
        self._output_path = Path(output_path).resolve() if output_path else None
        self._command_builder = command_builder
        self._show_settings = show_settings

        # Store custom keyboard shortcuts
        self._custom_open_keys = open_keys
        self._custom_play_stop_keys = play_stop_keys
        self._custom_settings_keys = settings_keys

        # Status state
        self._status_icon = initial_status_icon
        self._status_tooltip = initial_status_tooltip
        self._command_running = False

        # Spinner state
        self._spinner_frame_index = 0
        self._spinner_timer = None

        # Auto-generate ID if not provided
        widget_id = id or sanitize_id(name)

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
                display_name=self._command_name,
                command_builder=self._command_builder,
                _embedded=True,
            )
        else:
            self._name_widget = Static(self._command_name, classes="command-name")

        # Set tooltip on name widget with available keyboard shortcuts
        self._build_tooltip_with_shortcuts()

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

    def on_mount(self) -> None:
        """Set up runtime keyboard bindings."""
        # Open output bindings (only if output_path is set)
        if self._output_path:
            open_keys = self._custom_open_keys if self._custom_open_keys is not None else self.DEFAULT_OPEN_KEYS
            for key in open_keys:
                self._bindings.bind(key, "open_output", "Open output", show=False)

        # Play/stop bindings
        play_stop_keys = (
            self._custom_play_stop_keys if self._custom_play_stop_keys is not None else self.DEFAULT_PLAY_STOP_KEYS
        )
        for key in play_stop_keys:
            self._bindings.bind(key, "play_stop", "Play/Stop", show=False)

        # Settings bindings (if enabled)
        if self._show_settings:
            settings_keys = (
                self._custom_settings_keys if self._custom_settings_keys is not None else self.DEFAULT_SETTINGS_KEYS
            )
            for key in settings_keys:
                self._bindings.bind(key, "settings", "Settings", show=False)

    def on_click(self, event) -> None:
        """Handle clicks on child widgets."""
        event.stop()

        # Play/stop button
        if hasattr(event.widget, "_is_play_button"):
            if self._command_running:
                self.post_message(self.StopClicked(self, self._command_name, self._output_path))
            else:
                self.post_message(self.PlayClicked(self, self._command_name, self._output_path))

        # Settings icon
        elif event.widget == self._settings_widget if self._show_settings else False:
            self.post_message(self.SettingsClicked(self, self._command_name, self._output_path))

    def on_file_link_opened(self, event: FileLink.Opened) -> None:
        """Handle FileLink.Opened from embedded name widget."""
        # Re-post as OutputClicked for consistency
        if self._output_path:
            self.post_message(self.OutputClicked(self._output_path))

    # ------------------------------------------------------------------ #
    # Keyboard actions
    # ------------------------------------------------------------------ #
    def action_open_output(self) -> None:
        """Open output file (if set)."""
        if self._output_path and isinstance(self._name_widget, FileLink):
            self._name_widget.action_open_file()

    def action_play_stop(self) -> None:
        """Toggle play/stop."""
        if self._command_running:
            self.post_message(self.StopClicked(self, self._command_name, self._output_path))
        else:
            self.post_message(self.PlayClicked(self, self._command_name, self._output_path))

    def action_settings(self) -> None:
        """Open settings."""
        if self._show_settings:
            self.post_message(self.SettingsClicked(self, self._command_name, self._output_path))

    # ------------------------------------------------------------------ #
    # Helper methods
    # ------------------------------------------------------------------ #
    def _build_tooltip_with_shortcuts(self) -> None:
        """Build and set tooltip on name widget showing all available keyboard shortcuts."""
        shortcuts = []

        # Add output opening if available
        if self._output_path:
            open_keys = self._custom_open_keys or self.DEFAULT_OPEN_KEYS
            shortcuts.append(f"Open output {format_keyboard_shortcuts(open_keys)}")

        # Add play/stop
        play_stop_keys = self._custom_play_stop_keys or self.DEFAULT_PLAY_STOP_KEYS
        shortcuts.append(f"Play/Stop {format_keyboard_shortcuts(play_stop_keys)}")

        # Add settings if available
        if self._show_settings:
            settings_keys = self._custom_settings_keys or self.DEFAULT_SETTINGS_KEYS
            shortcuts.append(f"Settings {format_keyboard_shortcuts(settings_keys)}")

        # Combine into tooltip
        tooltip = f"{self._command_name}: " + ", ".join(shortcuts)
        self._name_widget.tooltip = tooltip

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
            # Update widget display (spinner will override if running)
            self._status_widget.update(icon)

        if tooltip is not None:
            self._status_tooltip = tooltip
            self._status_widget.tooltip = tooltip

        if running is not None:
            was_running = self._command_running
            self._command_running = running

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
                display_name=self._command_name,
                command_builder=self._command_builder,
                _embedded=True,
            )
            # Mount before settings widget if it exists, otherwise at end
            if self._show_settings:
                self.mount(self._name_widget, before=self._settings_widget)
            else:
                self.mount(self._name_widget)

        # Update tooltip to reflect new output path availability
        self._build_tooltip_with_shortcuts()

    def _animate_spinner(self) -> None:
        """Animate the spinner (called by timer)."""
        if self._command_running:
            frame = self.SPINNER_FRAMES[self._spinner_frame_index]
            self._status_widget.update(frame)
            self._spinner_frame_index = (self._spinner_frame_index + 1) % len(self.SPINNER_FRAMES)

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def name(self) -> str:
        """Get command name."""
        return self._command_name

    @property
    def output_path(self) -> Path | None:
        """Get output file path."""
        return self._output_path

    @property
    def is_running(self) -> bool:
        """Check if command is currently running."""
        return self._command_running
