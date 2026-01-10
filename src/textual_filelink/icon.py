"""Icon dataclass for FileLinkWithIcons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Icon:
    """Configuration for an icon in FileLinkWithIcons.

    Attributes
    ----------
    name : str
        REQUIRED: Unique identifier for this icon within the widget
    icon : str
        REQUIRED: Unicode character to display (e.g., "✅", "⚙️", "🔒")
    tooltip : Optional[str]
        Optional tooltip text shown on hover
    clickable : bool
        Whether clicking this icon emits IconClicked events (default: False)
    key : Optional[str]
        Optional keyboard shortcut to trigger this icon (e.g., "1", "s", "ctrl+x")
    visible : bool
        Whether the icon is initially visible (default: True)

    Examples
    --------
    >>> Icon(name="status", icon="✅", tooltip="Passed")
    Icon(name='status', icon='✅', tooltip='Passed', clickable=False, key=None, visible=True)

    >>> Icon(name="settings", icon="⚙️", clickable=True, key="s")
    Icon(name='settings', icon='⚙️', tooltip=None, clickable=True, key='s', visible=True)

    >>> Icon(name="warning", icon="⚠️", visible=False)
    Icon(name='warning', icon='⚠️', tooltip=None, clickable=False, key=None, visible=False)

    Raises
    ------
    ValueError
        If name or icon is empty/None after initialization
    """

    name: str
    icon: str
    tooltip: Optional[str] = None
    clickable: bool = False
    key: Optional[str] = None
    visible: bool = True

    def __post_init__(self):
        """Validate icon configuration after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Icon name cannot be empty or whitespace-only")
        if not self.icon or not self.icon.strip():
            raise ValueError("Icon character cannot be empty or whitespace-only")
