from __future__ import annotations

import logging
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Literal

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from .file_link import FileLink

logger = logging.getLogger(__name__)


@dataclass
class IconConfig:
    """Configuration for a status icon in ToggleableFileLink."""

    name: str
    icon: str
    position: Literal["before", "after"] = "before"
    index: int | None = None
    visible: bool = True
    clickable: bool = False
    tooltip: str | None = None


class ToggleableFileLink(Widget, can_focus=True):
    """A FileLink with optional toggle (☐/☑) on the left, multiple status icons, and optional remove (×) on the right.

    Event Bubbling Policy
    ---------------------
    - Internal click handlers stop event propagation with event.stop()
    - Widget-specific messages (Toggled, Removed, IconClicked) bubble up by default
    - Parent containers can handle or stop these messages as needed
    """

    BINDINGS = [
        Binding("o", "open_file", "Open file", show=False),
        Binding("space", "toggle", "Toggle", show=False),
        Binding("t", "toggle", "Toggle", show=False),
        Binding("delete", "remove", "Remove", show=False),
        Binding("x", "remove", "Remove", show=False),
        Binding("1", "icon_1", "Icon 1", show=False),
        Binding("2", "icon_2", "Icon 2", show=False),
        Binding("3", "icon_3", "Icon 3", show=False),
        Binding("4", "icon_4", "Icon 4", show=False),
        Binding("5", "icon_5", "Icon 5", show=False),
        Binding("6", "icon_6", "Icon 6", show=False),
        Binding("7", "icon_7", "Icon 7", show=False),
        Binding("8", "icon_8", "Icon 8", show=False),
        Binding("9", "icon_9", "Icon 9", show=False),
    ]

    DEFAULT_CSS = """
    ToggleableFileLink {
        height: auto;
        width: auto;
        min-width: 100%;
    }

    ToggleableFileLink:focus {
        background: $accent 20%;
        border: tall $accent;
    }

    ToggleableFileLink Horizontal {
        height: auto;
        width: auto;
        align: left middle;
    }

    ToggleableFileLink .toggle-static {
        width: 3;
        max-width: 3;
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
        width: 5;
        max-width: 5;
        height: auto;
        background: transparent;
        border: none;
        padding: 0;
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

    ToggleableFileLink .file-link-container FileLink {
        text-align: left;
    }

    ToggleableFileLink .remove-static {
        width: 3;
        max-width: 3;
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
        """Posted when the toggle state changes.

        Attributes
        ----------
        path : Path
            The file path of the toggled widget.
        is_toggled : bool
            The new toggle state (True if toggled on, False if toggled off).
        """

        def __init__(self, path: Path, is_toggled: bool) -> None:
            super().__init__()
            self.path = path
            self.is_toggled = is_toggled

    class Removed(Message):
        """Posted when the remove button is clicked.

        Attributes
        ----------
        path : Path
            The file path of the widget to be removed.
        """

        def __init__(self, path: Path) -> None:
            super().__init__()
            self.path = path

    class IconClicked(Message):
        """Posted when a status icon is clicked.

        Attributes
        ----------
        path : Path
            The file path of the widget containing the icon.
        icon_name : str
            The name identifier of the clicked icon.
        icon : str
            The icon character/emoji that was clicked.
        """

        def __init__(self, path: Path, icon_name: str, icon: str) -> None:
            super().__init__()
            self.path = path
            self.icon_name = icon_name
            self.icon = icon

    def __init__(
        self,
        path: Path | str,
        *,
        initial_toggle: bool = False,
        show_toggle: bool = True,
        show_remove: bool = True,
        icons: list[IconConfig | dict] | None = None,
        line: int | None = None,
        column: int | None = None,
        command_builder: Callable | None = None,
        disable_on_untoggle: bool = False,
        toggle_tooltip: str | None = None,
        remove_tooltip: str | None = None,
        link_tooltip: str | None = None,
        # Deprecated parameters for backwards compatibility
        status_icon: str | None = None,
        status_icon_clickable: bool = False,
        status_tooltip: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
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
        icons : list[IconConfig | dict] | None
            List of icon configurations. Each can be an IconConfig dataclass or a dict with keys:
            - name (str, required): Unique identifier for the icon
            - icon (str, required): Unicode character to display
            - position (str, optional): "before" or "after" the filename (default: "before")
            - index (int | None, optional): Explicit ordering index (default: None = use list order)
            - visible (bool, optional): Whether icon is initially visible (default: True)
            - clickable (bool, optional): Whether icon posts IconClicked messages (default: False)
            - tooltip (str | None, optional): Tooltip text (default: None)
        line, column : int | None
            Optional cursor position to jump to.
        command_builder : Callable | None
            Function for opening the file.
        disable_on_untoggle : bool
            If True, dim/disable the link when untoggled.
        toggle_tooltip : str | None
            Tooltip text for the toggle button.
        remove_tooltip : str | None
            Tooltip text for the remove button.
        link_tooltip : str | None
            Tooltip text for the filename/link itself.
        status_icon : str | None
            [DEPRECATED] Use icons parameter instead. Unicode icon to display before filename.
        status_icon_clickable : bool
            [DEPRECATED] Use icons parameter instead.
        status_tooltip : str | None
            [DEPRECATED] Use icons parameter instead.
        """
        super().__init__(name=name, id=id, classes=classes)
        self._path = Path(path).resolve()
        self._is_toggled = initial_toggle
        self._show_toggle = show_toggle
        self._show_remove = show_remove
        self._line = line
        self._column = column
        self._command_builder = command_builder
        self._disable_on_untoggle = disable_on_untoggle
        self._toggle_tooltip = toggle_tooltip
        self._remove_tooltip = remove_tooltip
        self._link_tooltip = link_tooltip
        logger.debug(
            f"ToggleableFileLink initialized with path: {self._path}, initial_toggle: {initial_toggle}, show_toggle: {show_toggle}, show_remove: {show_remove}"
        )

        # Handle backwards compatibility for old status_icon parameters
        if status_icon is not None:
            warnings.warn(
                "status_icon, status_icon_clickable, and status_tooltip are deprecated. "
                "Use the icons parameter instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if icons is None:
                icons = []
            icons.append(
                {
                    "name": "status",
                    "icon": status_icon,
                    "clickable": status_icon_clickable,
                    "tooltip": status_tooltip,
                    "position": "before",
                }
            )

        # Convert icons to IconConfig dataclasses and validate
        self._icons: list[IconConfig] = []
        if icons:
            self._icons = self._validate_and_convert_icons(icons)

    def _get_keys_for_action(self, action_name: str) -> list[str]:
        """Get all keys bound to an action.

        Args:
            action_name: The action name (e.g., 'open_file', 'toggle')

        Returns:
            List of key names bound to the action (e.g., ['o'], ['space', 't'])
        """
        keys = []
        for binding in self.BINDINGS:
            if binding.action == action_name:
                keys.append(binding.key)
        return keys

    def _enhance_tooltip(self, base_tooltip: str | None, action_name: str) -> str:
        """Enhance tooltip with keyboard shortcut hints.

        Args:
            base_tooltip: The base tooltip text (or None)
            action_name: The action name to get keys for

        Returns:
            Enhanced tooltip with keyboard shortcuts appended
        """
        keys = self._get_keys_for_action(action_name)

        if not keys:
            # No keys bound, return base tooltip or empty string
            return base_tooltip or ""

        # Format keys as "key1/key2/key3"
        key_hint = "/".join(keys)

        # If no base tooltip, generate sensible default
        if not base_tooltip:
            # Convert action_name to readable text
            readable = action_name.replace("_", " ").title()
            base_tooltip = readable

        return f"{base_tooltip} ({key_hint})"

    def _validate_and_convert_icons(self, icons: list[IconConfig | dict]) -> list[IconConfig]:
        """Validate and convert icon configs to IconConfig dataclasses."""
        result = []
        seen_names = set()

        for i, icon_data in enumerate(icons):
            # Convert dict to IconConfig if needed
            if isinstance(icon_data, dict):
                # Validate required fields
                if "name" not in icon_data:
                    raise ValueError(f"Icon at index {i} missing required field 'name'")
                if "icon" not in icon_data:
                    raise ValueError(f"Icon at index {i} missing required field 'icon'")

                # Validate position if provided
                position = icon_data.get("position", "before")
                if position not in ("before", "after"):
                    raise ValueError(
                        f"Icon '{icon_data['name']}' has invalid position '{position}'. Must be 'before' or 'after'."
                    )

                icon_config = IconConfig(**icon_data)
            elif isinstance(icon_data, IconConfig):
                icon_config = icon_data
            else:
                raise ValueError(f"Icon at index {i} must be IconConfig or dict, got {type(icon_data)}")

            # Check for duplicate names
            if icon_config.name in seen_names:
                raise ValueError(f"Duplicate icon name: '{icon_config.name}'")
            seen_names.add(icon_config.name)

            result.append(icon_config)

        return result

    def _sort_icons(self, icons: list[IconConfig], position: str) -> list[IconConfig]:
        """Sort icons by index (explicit first), then original list position, then name."""
        # Filter by position
        position_icons = [ic for ic in icons if ic.position == position]

        # Attach original position for stable sorting
        icons_with_pos = []
        for i, ic in enumerate(position_icons):
            icons_with_pos.append((i, ic))

        def sort_key(item):
            original_pos, ic = item
            idx = ic.index
            if idx is not None:
                return (0, idx, ic.name)  # Explicit indices first
            else:
                return (1, original_pos, ic.name)  # Then by list order, name for tiebreak

        sorted_icons = sorted(icons_with_pos, key=sort_key)
        return [ic for _, ic in sorted_icons]

    def compose(self) -> ComposeResult:
        with Horizontal():
            # Toggle
            if self._show_toggle:
                toggle_static = Static(
                    "☑" if self._is_toggled else "☐",
                    id="toggle",
                    classes="toggle-static",
                )
                toggle_static.tooltip = self._enhance_tooltip(self._toggle_tooltip, "toggle")
                yield toggle_static

            # Icons before filename
            before_icons = self._sort_icons(self._icons, "before")
            for icon_config in before_icons:
                if icon_config.visible:
                    yield self._create_icon_static(icon_config)

            # FileLink (with _embedded=True to prevent focus stealing)
            # Enhance tooltip with keyboard shortcut for open action
            enhanced_tooltip = self._enhance_tooltip(self._link_tooltip, "open_file")
            yield FileLink(
                self._path,
                line=self._line,
                column=self._column,
                command_builder=self._command_builder,
                classes="file-link-container",
                _embedded=True,
                tooltip=enhanced_tooltip if enhanced_tooltip else None,
            )

            # Icons after filename
            after_icons = self._sort_icons(self._icons, "after")
            for icon_config in after_icons:
                if icon_config.visible:
                    yield self._create_icon_static(icon_config)

            # Remove button
            if self._show_remove:
                remove_static = Static(
                    "×",
                    id="remove",
                    classes="remove-static",
                )
                remove_static.tooltip = self._enhance_tooltip(self._remove_tooltip, "remove")
                yield remove_static

    def _create_icon_static(self, icon_config: IconConfig) -> Static:
        """Create a Static widget for an icon."""
        classes = "status-icon"
        if icon_config.clickable:
            classes += " clickable"

        static = Static(
            icon_config.icon,
            id=f"icon-{icon_config.name}",
            classes=classes,
        )

        # Enhance tooltip with keyboard shortcut if clickable or special icons
        if icon_config.name == "settings":
            # Special case: settings uses 's' key, not a number
            static.tooltip = self._enhance_tooltip(icon_config.tooltip, "settings")
        elif icon_config.name == "play_stop":
            # Special case: play_stop uses 'p' and 'space' keys, not a number
            static.tooltip = self._enhance_tooltip(icon_config.tooltip, "play_stop")
        elif icon_config.clickable:
            # Find which number key activates this icon
            clickable_icons = [ic for ic in self._icons if ic.clickable and ic.visible]
            try:
                icon_index = clickable_icons.index(icon_config)
                icon_number = icon_index + 1  # 1-indexed
                if icon_number <= 9:
                    action_name = f"icon_{icon_number}"
                    static.tooltip = self._enhance_tooltip(icon_config.tooltip, action_name)
                else:
                    # No keyboard shortcut for icons beyond 9
                    static.tooltip = icon_config.tooltip or ""
            except ValueError:
                static.tooltip = icon_config.tooltip or ""
        else:
            static.tooltip = icon_config.tooltip or ""

        return static

    def on_mount(self) -> None:
        """Update initial disabled state."""
        self._update_disabled_state()

    def _update_disabled_state(self) -> None:
        """Update the disabled class based on toggle state."""
        if self._disable_on_untoggle and not self._is_toggled:
            self.add_class("disabled")
        else:
            self.remove_class("disabled")

    def set_icon_visible(self, name: str, visible: bool) -> None:
        """Show or hide a specific icon.

        Parameters
        ----------
        name : str
            The name of the icon to show/hide.
        visible : bool
            True to show, False to hide.

        Raises
        ------
        KeyError
            If no icon with the given name exists.
        """
        icon_config = self._get_icon_config(name)
        if icon_config is None:
            raise KeyError(f"No icon with name '{name}' found")

        icon_config.visible = visible

        # Update the DOM
        try:
            icon_static = self.query_one(f"#icon-{name}", Static)
            icon_static.display = visible
        except Exception:
            # Icon not yet mounted, will be handled in compose
            pass

    def update_icon(self, name: str, **kwargs) -> None:
        """Update properties of an existing icon.

        Parameters
        ----------
        name : str
            The name of the icon to update.
        **kwargs
            Properties to update: icon, position, index, visible, clickable, tooltip

        Raises
        ------
        KeyError
            If no icon with the given name exists.
        ValueError
            If an invalid property value is provided.

        Examples
        --------
        >>> link.update_icon("status", icon="✓", tooltip="Complete")
        >>> link.update_icon("warning", visible=False)
        """
        icon_config = self._get_icon_config(name)
        if icon_config is None:
            raise KeyError(f"No icon with name '{name}' found")

        # Validate position if provided
        if "position" in kwargs:
            position = kwargs["position"]
            if position not in ("before", "after"):
                raise ValueError(f"Invalid position '{position}'. Must be 'before' or 'after'.")

        # Update the config
        for key, value in kwargs.items():
            if hasattr(icon_config, key):
                setattr(icon_config, key, value)
            else:
                raise ValueError(f"Invalid property '{key}' for IconConfig")

        # If position or index changed, we need to recompose
        if "position" in kwargs or "index" in kwargs:
            # Schedule the recompose as a background task
            self.call_later(self._recompose_icons)
        else:
            # Update existing static widget
            try:
                icon_static = self.query_one(f"#icon-{name}", Static)

                if "icon" in kwargs:
                    icon_static.update(kwargs["icon"])

                if "tooltip" in kwargs:
                    new_tooltip = kwargs["tooltip"]

                    # Enhance with appropriate action name
                    if icon_config.name == "settings":
                        # Special case: settings uses 's' key
                        icon_static.tooltip = self._enhance_tooltip(new_tooltip, "settings")
                    elif icon_config.name == "play_stop":
                        # Special case: play_stop uses 'p' and 'space' keys
                        icon_static.tooltip = self._enhance_tooltip(new_tooltip, "play_stop")
                    elif icon_config.clickable:
                        # Find which number key activates this icon
                        clickable_icons = [ic for ic in self._icons if ic.clickable and ic.visible]
                        try:
                            icon_index = clickable_icons.index(icon_config)
                            icon_number = icon_index + 1
                            if icon_number <= 9:
                                action_name = f"icon_{icon_number}"
                                icon_static.tooltip = self._enhance_tooltip(new_tooltip, action_name)
                            else:
                                icon_static.tooltip = new_tooltip or ""
                        except ValueError:
                            icon_static.tooltip = new_tooltip or ""
                    else:
                        icon_static.tooltip = new_tooltip or ""

                if "visible" in kwargs:
                    icon_static.display = kwargs["visible"]

                if "clickable" in kwargs:
                    if kwargs["clickable"]:
                        icon_static.add_class("clickable")
                    else:
                        icon_static.remove_class("clickable")

            except Exception:
                # Icon not yet mounted or needs recompose
                pass

    async def _recompose_icons(self) -> None:
        """Recompose the entire widget to reflect icon order changes."""
        # Get the horizontal container
        try:
            container = self.query_one(Horizontal)
        except Exception:
            return

        # Find the FileLink position before removing icons
        try:
            file_link = self.query_one(FileLink)
        except Exception:
            return

        # Remove all existing icon statics and await removal
        icons_to_remove = list(self.query(".status-icon"))
        for static in icons_to_remove:
            await static.remove()

        # Now recalculate FileLink index after removals
        try:
            file_link_index = list(container.children).index(file_link)
        except Exception:
            return

        # Insert before icons
        before_icons = self._sort_icons(self._icons, "before")
        for i, icon_config in enumerate(before_icons):
            if icon_config.visible:
                icon_static = self._create_icon_static(icon_config)
                # Calculate position: after toggle (if shown), before file_link
                insert_pos = (1 if self._show_toggle else 0) + i
                container.mount(icon_static, before=insert_pos)

        # Insert after icons (need to recalculate file_link_index after before icons)
        file_link_index = list(container.children).index(file_link)
        after_icons = self._sort_icons(self._icons, "after")
        for icon_config in after_icons:
            if icon_config.visible:
                icon_static = self._create_icon_static(icon_config)
                # Insert right after FileLink
                container.mount(icon_static, after=file_link_index)

    def get_icon(self, name: str) -> dict | None:
        """Get a copy of an icon's configuration.

        Parameters
        ----------
        name : str
            The name of the icon to retrieve.

        Returns
        -------
        dict | None
            A dictionary copy of the icon configuration, or None if not found.
        """
        icon_config = self._get_icon_config(name)
        if icon_config is None:
            return None
        return asdict(icon_config)

    def _get_icon_config(self, name: str) -> IconConfig | None:
        """Get the IconConfig object for a given name (internal use)."""
        for icon_config in self._icons:
            if icon_config.name == name:
                return icon_config
        return None

    def set_toggle_tooltip(self, tooltip: str | None) -> None:
        """Update the toggle button tooltip.

        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.
        """
        self._toggle_tooltip = tooltip
        try:
            toggle_static = self.query_one("#toggle", Static)
            toggle_static.tooltip = self._enhance_tooltip(tooltip, "toggle")
        except Exception:
            pass

    def set_remove_tooltip(self, tooltip: str | None) -> None:
        """Update the remove button tooltip.

        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.
        """
        self._remove_tooltip = tooltip
        try:
            remove_static = self.query_one("#remove", Static)
            remove_static.tooltip = self._enhance_tooltip(tooltip, "remove")
        except Exception:
            pass

    def set_link_tooltip(self, tooltip: str | None) -> None:
        """Update the filename/link tooltip.

        Parameters
        ----------
        tooltip : str | None
            New tooltip text, or None to remove tooltip.
        """
        self._link_tooltip = tooltip
        try:
            file_link = self.query_one(FileLink)
            file_link.tooltip = self._enhance_tooltip(tooltip, "open_file")
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
        toggle_static.update("☑" if self._is_toggled else "☐")

        # Update disabled state
        self._update_disabled_state()

        # Post message
        self.post_message(self.Toggled(self._path, self._is_toggled))

    @on(events.Click, ".status-icon")
    def _on_icon_clicked(self, event: events.Click) -> None:
        """Handle status icon click (if clickable)."""
        event.stop()  # Prevent bubbling

        # Extract icon name from ID
        target = event.control
        if not isinstance(target, Static):
            return

        icon_id = target.id
        if not icon_id or not icon_id.startswith("icon-"):
            return

        icon_name = icon_id[5:]  # Remove "icon-" prefix
        icon_config = self._get_icon_config(icon_name)

        if icon_config and icon_config.clickable:
            # Post message - it will automatically have self (ToggleableFileLink) as the sender
            self.post_message(self.IconClicked(self._path, icon_name, icon_config.icon))

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

    # ------------------------------------------------------------------ #
    # Keyboard handling
    # ------------------------------------------------------------------ #
    def action_open_file(self) -> None:
        """Open file via keyboard - delegate to child FileLink."""
        file_link = self.query_one(FileLink)
        file_link.action_open_file()

    def action_toggle(self) -> None:
        """Toggle via keyboard - reuse click logic."""
        if not self._show_toggle:
            return
        self._is_toggled = not self._is_toggled

        # Update static content
        toggle_static = self.query_one("#toggle", Static)
        toggle_static.update("☑" if self._is_toggled else "☐")

        # Update disabled state
        self._update_disabled_state()

        # Post message
        self.post_message(self.Toggled(self._path, self._is_toggled))

    def action_remove(self) -> None:
        """Remove via keyboard."""
        if not self._show_remove:
            return
        self.post_message(self.Removed(self._path))

    def action_icon_1(self) -> None:
        """Activate first clickable icon via keyboard."""
        self._activate_icon_by_index(0)

    def action_icon_2(self) -> None:
        """Activate second clickable icon via keyboard."""
        self._activate_icon_by_index(1)

    def action_icon_3(self) -> None:
        """Activate third clickable icon via keyboard."""
        self._activate_icon_by_index(2)

    def action_icon_4(self) -> None:
        """Activate fourth clickable icon via keyboard."""
        self._activate_icon_by_index(3)

    def action_icon_5(self) -> None:
        """Activate fifth clickable icon via keyboard."""
        self._activate_icon_by_index(4)

    def action_icon_6(self) -> None:
        """Activate sixth clickable icon via keyboard."""
        self._activate_icon_by_index(5)

    def action_icon_7(self) -> None:
        """Activate seventh clickable icon via keyboard."""
        self._activate_icon_by_index(6)

    def action_icon_8(self) -> None:
        """Activate eighth clickable icon via keyboard."""
        self._activate_icon_by_index(7)

    def action_icon_9(self) -> None:
        """Activate ninth clickable icon via keyboard."""
        self._activate_icon_by_index(8)

    def _activate_icon_by_index(self, index: int) -> None:
        """Helper to activate Nth clickable icon."""
        clickable_icons = [ic for ic in self._icons if ic.clickable and ic.visible]
        if 0 <= index < len(clickable_icons):
            icon_config = clickable_icons[index]
            self.post_message(self.IconClicked(self._path, icon_config.name, icon_config.icon))

    @property
    def is_toggled(self) -> bool:
        """Get the current toggle state."""
        return self._is_toggled

    @property
    def path(self) -> Path:
        """Get the file path."""
        return self._path

    @property
    def icons(self) -> list[dict]:
        """Get a list of all icon configurations (as dicts)."""
        return [asdict(ic) for ic in self._icons]

    @property
    def file_link(self) -> FileLink:
        """Get the internal FileLink widget."""
        return self.query_one(FileLink)
