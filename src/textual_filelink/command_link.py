from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import Callable

from textual import on
from textual.message import Message
from textual.timer import Timer

from .toggleable_file_link import ToggleableFileLink

logger = logging.getLogger(__name__)


class CommandLink(ToggleableFileLink):
    """A specialized widget for command orchestration and status display.

    Layout: [toggle] [status/spinner] [play/stop] command_name [settings] [remove]

    The widget is fully controlled by the parent - it displays state and emits
    events for user interactions. Single-instance commands only (not multiple
    concurrent runs of the same command).

    Event Bubbling Policy
    ---------------------
    - Internal click handlers stop event propagation with event.stop()
    - Widget-specific messages (PlayClicked, StopClicked, SettingsClicked) bubble up by default
    - Parent containers can handle or stop these messages as needed

    Example:
        ```python
        link = CommandLink(
            "Tests",
            output_path=None,
            initial_status_icon="❓",
            initial_status_tooltip="Not run",
        )

        # When command starts
        link.set_status(running=True, tooltip="Running tests...")

        # When command completes
        link.set_status(icon="✅", running=False, tooltip="Passed")
        link.set_output_path(Path("test_output.log"))
        ```
    """

    # Spinner frames for animation
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    class PlayClicked(Message):
        """Posted when play button is clicked.

        Attributes
        ----------
        path : Path | None
            The output file path, or None if not set.
        name : str
            The command name.
        output_path : Path | None
            The output file path (same as path for consistency).
        is_toggled : bool
            Whether the command is toggled/selected.
        """

        def __init__(self, path: Path | None, name: str, output_path: Path | None, is_toggled: bool) -> None:
            super().__init__()
            self.path = path
            self.name = name
            self.output_path = output_path
            self.is_toggled = is_toggled

    class StopClicked(Message):
        """Posted when stop button is clicked.

        Attributes
        ----------
        path : Path | None
            The output file path, or None if not set.
        name : str
            The command name.
        output_path : Path | None
            The output file path (same as path for consistency).
        is_toggled : bool
            Whether the command is toggled/selected.
        """

        def __init__(self, path: Path | None, name: str, output_path: Path | None, is_toggled: bool) -> None:
            super().__init__()
            self.path = path
            self.name = name
            self.output_path = output_path
            self.is_toggled = is_toggled

    class SettingsClicked(Message):
        """Posted when settings icon is clicked.

        Attributes
        ----------
        path : Path | None
            The output file path, or None if not set.
        name : str
            The command name.
        output_path : Path | None
            The output file path (same as path for consistency).
        is_toggled : bool
            Whether the command is toggled/selected.
        """

        def __init__(self, path: Path | None, name: str, output_path: Path | None, is_toggled: bool) -> None:
            super().__init__()
            self.path = path
            self.name = name
            self.output_path = output_path
            self.is_toggled = is_toggled

    def __init__(
        self,
        name: str,
        output_path: Path | str | None = None,
        *,
        initial_toggle: bool = False,
        initial_status_icon: str = "❓",
        initial_status_tooltip: str | None = None,
        running: bool = False,
        show_toggle: bool = True,
        show_settings: bool = True,
        show_remove: bool = True,
        toggle_tooltip: str | None = None,
        settings_tooltip: str | None = None,
        remove_tooltip: str | None = None,
        command_builder: Callable | None = None,
        disable_on_untoggle: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        name : str
            Command display name (also used as widget ID).
        output_path : Path | str | None
            Path to output file. If None, clicking command name does nothing.
        initial_toggle : bool
            Whether the command starts toggled/selected (default: False).
        initial_status_icon : str
            Initial status icon (default: "❓" for not run).
        initial_status_tooltip : str | None
            Initial tooltip for status icon.
        running : bool
            Whether command is currently running (default: False).
            If True, shows spinner and stop button instead of status icon and play button.
        show_toggle : bool
            Whether to show the toggle checkbox (default: True).
        show_settings : bool
            Whether to show the settings icon (default: True).
        show_remove : bool
            Whether to show the remove button (default: True).
        toggle_tooltip : str | None
            Tooltip for toggle checkbox.
        settings_tooltip : str | None
            Tooltip for settings icon.
        remove_tooltip : str | None
            Tooltip for remove button.
        command_builder : Callable | None
            Custom command builder for opening output files.
        disable_on_untoggle : bool
            If True, dim/disable when untoggled (default: False).
        """
        self._name = name
        self._output_path = Path(output_path) if output_path else None
        self._command_running = running  # Set BEFORE calling super().__init__()
        self._show_settings = show_settings
        self._status_icon = initial_status_icon
        self._status_tooltip = initial_status_tooltip
        self._spinner_timer: Timer | None = None
        self._spinner_frame = 0

        logger.debug(
            f"Initializing CommandLink: {self._name}, running={self._command_running}, output_path={self._output_path}"
        )

        # Build icons list for parent ToggleableFileLink
        icons = []

        # Status icon (or will be replaced by spinner if running)
        icons.append(
            {
                "name": "status",
                "icon": initial_status_icon,
                "tooltip": initial_status_tooltip,
                "position": "before",
                "index": 0,
                "visible": not running,  # Hide if running (spinner will show instead)
            }
        )

        # Play/Stop button
        play_stop_icon = "⏹️" if running else "▶️"
        play_stop_tooltip = "Stop command" if running else "Run command"
        icons.append(
            {
                "name": "play_stop",
                "icon": play_stop_icon,
                "tooltip": play_stop_tooltip,
                "position": "before",
                "index": 1,
                "clickable": True,
            }
        )

        # Settings icon (after command name)
        if show_settings:
            icons.append(
                {
                    "name": "settings",
                    "icon": "⚙",
                    "tooltip": settings_tooltip or "Settings",
                    "position": "after",
                    "index": 0,
                    "clickable": True,
                }
            )

        # Determine command builder - use no-op if no output path
        if output_path is None and command_builder is None:
            command_builder = CommandLink._noop_command_builder

        # Use command name as display text (parent will show path.name)
        display_path = Path(name)

        # Initialize parent
        super().__init__(
            display_path,
            initial_toggle=initial_toggle,
            show_toggle=show_toggle,
            show_remove=show_remove,
            icons=icons,
            toggle_tooltip=toggle_tooltip,
            remove_tooltip=remove_tooltip,
            command_builder=command_builder,
            disable_on_untoggle=disable_on_untoggle,
            id=name,  # Use name as ID for easy lookup
            name=None,  # Don't set Widget.name, we use our own _name
        )

        logger.debug(
            f"CommandLink after super init: {self._name}, running={self._command_running}, output_path={self._output_path}"
        )

    @staticmethod
    def _noop_command_builder(_path: Path, _line: int | None, _column: int | None) -> list[str]:
        """No-op command builder when no output file exists."""
        return ["true"]  # Unix no-op command

    def set_status(
        self,
        icon: str | None = None,
        tooltip: str | None = None,
        running: bool | None = None,
    ) -> None:
        """Update command status display.

        Parameters
        ----------
        icon : str | None
            Status icon to display. If None and running=True, shows spinner.
        tooltip : str | None
            Tooltip for status icon/spinner.
        running : bool | None
            Update running state. If True, shows stop button; if False, shows play button.

        Examples
        --------
        >>> link.set_status(running=True, tooltip="Running tests...")
        >>> link.set_status(icon="✅", running=False, tooltip="All tests passed")
        >>> link.set_status(icon="❌", tooltip="3 tests failed")  # Update icon only
        """
        # Update running state
        if running is not None:
            self._command_running = running
            logger.debug(f"CommandLink '{self._name}' running state set to {running}")

            # Update play/stop button
            play_stop_icon = "⏹️" if running else "▶️"
            play_stop_tooltip = "Stop command" if running else "Run command"
            self.update_icon("play_stop", icon=play_stop_icon, tooltip=play_stop_tooltip)

        # Update status icon/spinner
        if icon is not None:
            self._status_icon = icon
            self._status_tooltip = tooltip
            # Show the icon (stop spinner if it was showing)
            self._stop_spinner()
            self.set_icon_visible("status", True)
            self.update_icon("status", icon=icon, tooltip=tooltip)
        elif tooltip is not None:
            # Update tooltip only
            self._status_tooltip = tooltip
            if self.get_icon("status")["visible"]:
                self.update_icon("status", tooltip=tooltip)

        # Handle spinner visibility
        if running is not None:
            if running and icon is None:
                # Show spinner, hide status icon
                self.set_icon_visible("status", False)
                self._start_spinner()
            elif not running:
                # Stop spinner, show status icon
                self._stop_spinner()
                self.set_icon_visible("status", True)
                if self._status_icon:
                    self.update_icon("status", icon=self._status_icon, tooltip=self._status_tooltip)

    def _start_spinner(self) -> None:
        """Start the spinner animation."""
        if self._spinner_timer is None:
            self._spinner_frame = 0
            # Update immediately
            self.update_icon("status", icon=self.SPINNER_FRAMES[0], tooltip=self._status_tooltip)
            self.set_icon_visible("status", True)
            # Start timer for animation (10 FPS)
            self._spinner_timer = self.set_interval(0.1, self._animate_spinner)

    def _stop_spinner(self) -> None:
        """Stop the spinner animation."""
        if self._spinner_timer is not None:
            self._spinner_timer.stop()
            self._spinner_timer = None
            self._spinner_frame = 0

    def _animate_spinner(self) -> None:
        """Animate the spinner by cycling through frames."""
        self._spinner_frame = (self._spinner_frame + 1) % len(self.SPINNER_FRAMES)
        try:
            self.update_icon("status", icon=self.SPINNER_FRAMES[self._spinner_frame])
        except KeyError:
            # Icon was removed, stop the spinner
            self._stop_spinner()

    def set_output_path(
        self,
        path: Path | str | None,
        tooltip: str | None = None,
    ) -> None:
        """Update the output file path and optionally its tooltip.

        Parameters
        ----------
        path : Path | str | None
            New output file path. If None, clicking command name does nothing.
        tooltip : str | None
            New tooltip for the command name/file link.

        Examples
        --------
        >>> link.set_output_path(Path("output.log"), tooltip="Click to view output")
        >>> link.set_output_path(None)  # Clear output path
        """
        self._output_path = Path(path) if path else None

        # Update the internal FileLink via the new property (only if mounted)
        try:
            file_link = self.file_link
            file_link._path = self._output_path if self._output_path else Path(self._name)

            # Update command builder
            if self._output_path is None:
                file_link._command_builder = CommandLink._noop_command_builder
            else:
                file_link._command_builder = None  # Use default

            # Update tooltip if provided
            if tooltip is not None:
                file_link.tooltip = tooltip
        except Exception:
            # Widget not mounted yet, changes will apply when mounted
            pass

    def set_toggle(
        self,
        toggled: bool,
        tooltip: str | None = None,
    ) -> None:
        """Update toggle state and optionally its tooltip.

        Parameters
        ----------
        toggled : bool
            New toggle state.
        tooltip : str | None
            New tooltip for the toggle checkbox.

        Examples
        --------
        >>> link.set_toggle(True, tooltip="Selected for batch run")
        >>> link.set_toggle(False)
        """
        # Update internal state
        self._is_toggled = toggled

        # Update the toggle display
        try:
            toggle_static = self.query_one("#toggle")
            toggle_static.update("☑" if toggled else "☐")

            if tooltip is not None:
                toggle_static.tooltip = tooltip
        except Exception:
            pass

        # Update disabled state if needed
        self._update_disabled_state()

    def set_settings_tooltip(self, tooltip: str | None) -> None:
        """Update settings icon tooltip.

        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.

        Examples
        --------
        >>> link.set_settings_tooltip("Configure test options")
        """
        if self._show_settings:
            with contextlib.suppress(KeyError):
                self.update_icon("settings", tooltip=tooltip or "Settings")

    def on_unmount(self) -> None:
        """Clean up spinner timer when widget is unmounted."""
        self._stop_spinner()

    @on(ToggleableFileLink.IconClicked)
    def _handle_icon_click(self, event: ToggleableFileLink.IconClicked) -> None:
        """Handle icon clicks - convert to CommandLink-specific messages."""
        icon_name = event.icon_name

        # Stop the event from bubbling further
        event.stop()

        if icon_name == "play_stop":
            if self._command_running:
                self.post_message(
                    self.StopClicked(
                        path=self._output_path,
                        name=self.name,
                        output_path=self._output_path,
                        is_toggled=self._is_toggled,
                    )
                )
            else:
                self.post_message(
                    self.PlayClicked(
                        path=self._output_path,
                        name=self.name,
                        output_path=self._output_path,
                        is_toggled=self._is_toggled,
                    )
                )
        elif icon_name == "settings":
            self.post_message(
                self.SettingsClicked(
                    path=self._output_path, name=self.name, output_path=self._output_path, is_toggled=self._is_toggled
                )
            )

    @property
    def display_name(self) -> str:
        """Get the command display name.

        Returns
        -------
        str
            The command name used for display.
        """
        return self._name

    @property
    def name(self) -> str:
        """Get the command name (alias for display_name).

        Returns
        -------
        str
            The command name.
        """
        return self.id or self._name

    @property
    def path(self) -> Path | None:
        """Get the output file path.

        This overrides the parent's path property to return the actual
        output file path instead of a display path.

        Returns
        -------
        Path | None
            The output file path, or None if not set.
        """
        return self._output_path

    @property
    def output_path(self) -> Path | None:
        """Get the current output file path.

        Returns
        -------
        Path | None
            The output file path, or None if not set.
        """
        return self._output_path

    @property
    def is_running(self) -> bool:
        """Get whether the command is currently running."""
        return self._command_running
