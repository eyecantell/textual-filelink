from __future__ import annotations

from pathlib import Path
from typing import Optional, Callable

from textual import on, events
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static
from textual.message import Message
from textual.containers import Horizontal

from .file_link import FileLink


class ToggleableFileLink(Widget):
    """A FileLink with an optional toggle (☐/✓) on the left, optional status icon, and optional remove (×) on the right."""

    DEFAULT_CSS = """
    ToggleableFileLink {
        height: auto;
        width: 100%;
    }
    
    ToggleableFileLink Horizontal {
        height: auto;
        width: 100%;
        align: left middle;
    }
    
    ToggleableFileLink .toggle-static {
        width: 3;
        min-width: 3;
        height: auto;
        background: transparent;
        border: none;
        padding: 0;
        color: $text;
        content-align: center middle;
    }
    
    ToggleableFileLink .toggle-static:hover {
        background: $boost;
    }
    
    ToggleableFileLink .status-icon {
        width: auto;
        min-width: 2;
        height: auto;
        background: transparent;
        border: none;
        padding: 0 1 0 0;
        color: $text;
        content-align: center middle;
    }
    
    ToggleableFileLink .status-icon:hover {
        background: $boost;
    }
    
    ToggleableFileLink .status-icon.clickable {
        text-style: underline;
    }
    
    ToggleableFileLink .file-link-container {
        width: 1fr;
        height: auto;
    }
    
    ToggleableFileLink .remove-static {
        width: 3;
        min-width: 3;
        height: auto;
        background: transparent;
        border: none;
        padding: 0;
        color: $error;
        content-align: center middle;
    }
    
    ToggleableFileLink .remove-static:hover {
        background: $boost;
        color: $error;
    }
    
    ToggleableFileLink.disabled {
        opacity: 0.5;
    }
    
    ToggleableFileLink.disabled .file-link-container {
        text-style: dim;
    }
    """

    class Toggled(Message):
        """Posted when the toggle state changes."""
        def __init__(self, path: Path, is_toggled: bool) -> None:
            super().__init__()
            self.path = path
            self.is_toggled = is_toggled

    class Removed(Message):
        """Posted when the remove button is clicked."""
        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    class StatusIconClicked(Message):
        """Posted when the status icon is clicked."""
        def __init__(self, path: Path, icon: str) -> None:
            super().__init__()
            self.path = path
            self.icon = icon

    def __init__(
        self,
        path: Path | str,
        *,
        initial_toggle: bool = False,
        show_toggle: bool = True,
        show_remove: bool = True,
        status_icon: Optional[str] = None,
        status_icon_clickable: bool = False,
        line: Optional[int] = None,
        column: Optional[int] = None,
        command_builder: Optional[Callable] = None,
        disable_on_untoggle: bool = False,
        toggle_tooltip: Optional[str] = None,
        status_tooltip: Optional[str] = None,
        remove_tooltip: Optional[str] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        path : Path | str
            Full path to the file.
        initial_toggle : bool
            Whether the item starts toggled (checked).
        show_toggle : bool
            Whether to display the toggle component (default: True).
        show_remove : bool
            Whether to display the remove component (default: True).
        status_icon : str | None
            Optional unicode icon to display before the filename.
        status_icon_clickable : bool
            Whether the status icon should be clickable and post StatusIconClicked messages.
        line, column : int | None
            Optional cursor position to jump to.
        command_builder : Callable | None
            Function for opening the file.
        disable_on_untoggle : bool
            If True, dim/disable the link when untoggled.
        toggle_tooltip : str | None
            Tooltip text for the toggle button.
        status_tooltip : str | None
            Tooltip text for the status icon.
        remove_tooltip : str | None
            Tooltip text for the remove button.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._path = Path(path).resolve()
        self._is_toggled = initial_toggle
        self._show_toggle = show_toggle
        self._show_remove = show_remove
        self._status_icon = status_icon
        self._status_icon_clickable = status_icon_clickable
        self._line = line
        self._column = column
        self._command_builder = command_builder
        self._disable_on_untoggle = disable_on_untoggle
        self._toggle_tooltip = toggle_tooltip
        self._status_tooltip = status_tooltip
        self._remove_tooltip = remove_tooltip

    def compose(self) -> ComposeResult:
        with Horizontal():
            if self._show_toggle:
                toggle_static = Static(
                    "✓" if self._is_toggled else "☐",
                    id="toggle",
                    classes="toggle-static",
                )
                if self._toggle_tooltip:
                    toggle_static.tooltip = self._toggle_tooltip
                yield toggle_static
            
            if self._status_icon:
                status_classes = "status-icon"
                if self._status_icon_clickable:
                    status_classes += " clickable"
                
                status_static = Static(
                    self._status_icon,
                    id="status-icon",
                    classes=status_classes,
                )
                if self._status_tooltip:
                    status_static.tooltip = self._status_tooltip
                yield status_static
            
            yield FileLink(
                self._path,
                line=self._line,
                column=self._column,
                command_builder=self._command_builder,
                classes="file-link-container",
            )
            
            if self._show_remove:
                remove_static = Static(
                    "×",
                    id="remove",
                    classes="remove-static",
                )
                if self._remove_tooltip:
                    remove_static.tooltip = self._remove_tooltip
                yield remove_static

    def on_mount(self) -> None:
        """Update initial disabled state."""
        self._update_disabled_state()

    def _update_disabled_state(self) -> None:
        """Update the disabled class based on toggle state."""
        if self._disable_on_untoggle and not self._is_toggled:
            self.add_class("disabled")
        else:
            self.remove_class("disabled")

    def set_status_icon(self, icon: Optional[str], tooltip: Optional[str] = None) -> None:
        """Update the status icon and optionally its tooltip.
        
        Parameters
        ----------
        icon : str | None
            New icon to display, or None to hide the icon.
        tooltip : str | None
            Optional new tooltip text. If not provided, keeps existing tooltip.
        """
        self._status_icon = icon
        if tooltip is not None:
            self._status_tooltip = tooltip
        
        # Try to update existing icon if it exists
        try:
            status_static = self.query_one("#status-icon", Static)
            if icon:
                status_static.update(icon)
                status_static.display = True
                if tooltip is not None:
                    status_static.tooltip = tooltip
            else:
                status_static.display = False
        except Exception:
            # Icon doesn't exist yet (shouldn't happen after mount, but handle gracefully)
            pass

    def set_toggle_tooltip(self, tooltip: Optional[str]) -> None:
        """Update the toggle button tooltip.
        
        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.
        """
        self._toggle_tooltip = tooltip
        try:
            toggle_static = self.query_one("#toggle", Static)
            toggle_static.tooltip = tooltip or ""
        except Exception:
            pass

    def set_remove_tooltip(self, tooltip: Optional[str]) -> None:
        """Update the remove button tooltip.
        
        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.
        """
        self._remove_tooltip = tooltip
        try:
            remove_static = self.query_one("#remove", Static)
            remove_static.tooltip = tooltip or ""
        except Exception:
            pass

    @on(events.Click, "#toggle")
    def _on_toggle_clicked(self, event: events.Click) -> None:
        """Handle toggle click (if shown)."""
        if not self._show_toggle:
            return
        event.stop()  # Prevent bubbling
        self._is_toggled = not self._is_toggled
        
        # Update static content
        toggle_static = self.query_one("#toggle", Static)
        toggle_static.update("✓" if self._is_toggled else "☐")
        
        # Update disabled state
        self._update_disabled_state()
        
        # Post message
        self.post_message(self.Toggled(self._path, self._is_toggled))

    @on(events.Click, "#status-icon")
    def _on_status_icon_clicked(self, event: events.Click) -> None:
        """Handle status icon click (if clickable)."""
        if not self._status_icon_clickable or not self._status_icon:
            return
        event.stop()  # Prevent bubbling
        self.post_message(self.StatusIconClicked(self._path, self._status_icon))

    @on(events.Click, "#remove")
    def _on_remove_clicked(self, event: events.Click) -> None:
        """Handle remove click (if shown)."""
        if not self._show_remove:
            return
        event.stop()  # Prevent bubbling
        self.post_message(self.Removed(self._path))

    @on(FileLink.Clicked)
    def _on_file_clicked(self, event: FileLink.Clicked) -> None:
        """Handle file link click - prevent if disabled."""
        if self._disable_on_untoggle and not self._is_toggled:
            event.stop()
        # Otherwise let it bubble up

    @property
    def is_toggled(self) -> bool:
        """Get the current toggle state."""
        return self._is_toggled

    @property
    def path(self) -> Path:
        """Get the file path."""
        return self._path
    
    @property
    def status_icon(self) -> Optional[str]:
        """Get the current status icon."""
        return self._status_icon