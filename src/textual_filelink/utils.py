"""Utility functions for textual-filelink."""

import re
import shlex
from pathlib import Path
from typing import Callable

# Allowed template variables for command_from_template
ALLOWED_VARIABLES = {
    "path",
    "path_relative",
    "path_name",
    "line",
    "column",
    "line_colon",
    "column_colon",
    "line_plus",
    "column_plus",
}


def sanitize_id(name: str) -> str:
    """Convert name to valid widget ID.

    Sanitizes for use as Textual widget ID: lowercase, spaces→hyphens,
    path separators→hyphens, keep only alphanumeric/hyphens/underscores.

    Parameters
    ----------
    name : str
        Name to sanitize (can contain spaces, paths, special characters)

    Returns
    -------
    str
        Sanitized ID containing only lowercase alphanumeric characters,
        hyphens, and underscores

    Examples
    --------
    >>> sanitize_id("Run Tests")
    'run-tests'
    >>> sanitize_id("src/main.py")
    'src-main-py'
    >>> sanitize_id("Build Project!")
    'build-project-'
    >>> sanitize_id("src\\\\file.py")
    'src-file-py'
    """
    # Convert to lowercase
    sanitized = name.lower()

    # Replace spaces and path separators with hyphens
    sanitized = sanitized.replace(" ", "-")
    sanitized = sanitized.replace("/", "-")
    sanitized = sanitized.replace("\\", "-")

    # Keep only alphanumeric, hyphens, and underscores
    return "".join(c if c.isalnum() or c in ("-", "_") else "-" for c in sanitized)


def format_keyboard_shortcuts(keys: list[str]) -> str:
    """Format keyboard shortcuts as (key1/key2/key3).

    Parameters
    ----------
    keys : list[str]
        List of keyboard shortcut keys.

    Returns
    -------
    str
        Formatted string like "(enter/o)" or empty string if no keys.

    Examples
    --------
    >>> format_keyboard_shortcuts(["enter", "o"])
    '(enter/o)'
    >>> format_keyboard_shortcuts(["space", "p"])
    '(space/p)'
    >>> format_keyboard_shortcuts([])
    ''
    """
    if not keys:
        return ""
    return f"({'/'.join(keys)})"


def format_duration(secs: float) -> str:
    """Format seconds into a human-readable duration string.

    Parameters
    ----------
    secs : float
        Number of seconds to format

    Returns
    -------
    str
        Human-readable string like "452ms", "2.4s", "1m 23s", "2h 5m", "1d 3h", "2w 3d"

    Examples
    --------
    >>> format_duration(0.5)
    '500ms'
    >>> format_duration(90)
    '1m 30s'
    >>> format_duration(3661)
    '1h 1m'
    """
    # Handle negative values (clock skew)
    if secs < 0:
        return ""

    # Milliseconds for sub-second durations
    if secs < 1:
        return f"{secs * 1000:.0f}ms"

    # Decimal seconds for 1-60s range
    if secs < 60:
        return f"{secs:.1f}s"

    # Minutes and seconds
    mins, secs_remainder = divmod(int(secs), 60)
    if mins < 60:
        return f"{mins}m {secs_remainder}s"

    # Hours and minutes
    hrs, mins_remainder = divmod(mins, 60)
    if hrs < 24:
        return f"{hrs}h {mins_remainder}m"

    # Days and hours
    days, hrs_remainder = divmod(hrs, 24)
    if days < 7:
        return f"{days}d {hrs_remainder}h"

    # Weeks and days
    weeks, days_remainder = divmod(days, 7)
    return f"{weeks}w {days_remainder}d" if days_remainder else f"{weeks}w"


def format_time_ago(secs: float) -> str:
    """Format elapsed seconds as time-ago string.

    Parameters
    ----------
    secs : float
        Number of seconds since event

    Returns
    -------
    str
        Human-readable string like "5s ago", "2m ago", "3h ago", "2d ago", "1w ago"

    Examples
    --------
    >>> format_time_ago(30)
    '30s ago'
    >>> format_time_ago(3661)
    '1h ago'
    """
    # Handle negative values (clock skew)
    if secs < 0:
        return ""

    # Seconds
    if secs < 60:
        return f"{int(secs)}s ago"

    # Minutes
    mins = int(secs) // 60
    if mins < 60:
        return f"{mins}m ago"

    # Hours
    hrs = mins // 60
    if hrs < 24:
        return f"{hrs}h ago"

    # Days
    days = hrs // 24
    if days < 7:
        return f"{days}d ago"

    # Weeks
    weeks = days // 7
    return f"{weeks}w ago"


def command_from_template(template: str) -> Callable[[Path, int | None, int | None], list[str]]:
    """Create a command builder from a template string.

    Supports Jinja2-style template variables:
    - {{ path }} - Full absolute path
    - {{ path_relative }} - Path relative to cwd (falls back to absolute)
    - {{ path_name }} - Just the filename
    - {{ line }} - Line number (empty string if None)
    - {{ column }} - Column number (empty string if None)
    - {{ line_colon }} - `:line` format (empty if None)
    - {{ column_colon }} - `:column` format (empty if None)
    - {{ line_plus }} - `+line` format (empty if None)
    - {{ column_plus }} - `+column` format (empty if None)

    The rendered template is split using shlex.split() to handle spaces correctly.
    Use quotes in templates for paths with spaces: 'myeditor "{{ path }}"'

    Parameters
    ----------
    template : str
        Template string with {{ variable }} placeholders

    Returns
    -------
    Callable[[Path, int | None, int | None], list[str]]
        Command builder function that takes (path, line, column) and returns
        command arguments as a list of strings

    Raises
    ------
    ValueError
        If template contains unknown variables

    Examples
    --------
    >>> builder = command_from_template("code --goto {{ path }}:{{ line }}:{{ column }}")
    >>> builder(Path("file.py"), 10, 5)
    ['code', '--goto', '/abs/path/file.py:10:5']

    >>> builder = command_from_template("vim {{ line_plus }} {{ path }}")
    >>> builder(Path("file.py"), 42, None)
    ['vim', '+42', '/abs/path/file.py']

    >>> builder(Path("file.py"), None, None)
    ['vim', '/abs/path/file.py']

    Notes
    -----
    Templates work great for simple formats but have limitations with conditional
    logic. For complex cases (e.g., vim's cursor() call with column support), use
    a custom builder function instead.
    """
    # Validate template - find all {{ var }} patterns
    variables = re.findall(r"\{\{\s*(\w+)\s*\}\}", template)
    unknown = set(variables) - ALLOWED_VARIABLES

    if unknown:
        raise ValueError(f"Unknown template variables: {unknown}. Allowed: {sorted(ALLOWED_VARIABLES)}")

    def builder(path: Path, line: int | None, column: int | None) -> list[str]:
        """Build command from template with given path, line, and column."""
        # Compute path variants
        path_abs = str(path.resolve())
        try:
            path_rel = str(path.relative_to(Path.cwd()))
        except ValueError:
            # Can't make relative, use absolute
            path_rel = path_abs
        path_name = path.name

        # Start with the template
        rendered = template

        # Replace helper format variables first (before basic variables)
        # This prevents partial replacements like {{ line_colon }} → {{ :42 }}
        rendered = rendered.replace("{{ line_plus }}", f"+{line}" if line else "")
        rendered = rendered.replace("{{ column_plus }}", f"+{column}" if column else "")
        rendered = rendered.replace("{{ line_colon }}", f":{line}" if line else "")
        rendered = rendered.replace("{{ column_colon }}", f":{column}" if column else "")

        # Replace basic variables
        rendered = rendered.replace("{{ path_relative }}", path_rel)
        rendered = rendered.replace("{{ path_name }}", path_name)
        rendered = rendered.replace("{{ path }}", path_abs)
        rendered = rendered.replace("{{ line }}", str(line) if line else "")
        rendered = rendered.replace("{{ column }}", str(column) if column else "")

        # Also handle variations with different whitespace
        rendered = rendered.replace("{{line_plus}}", f"+{line}" if line else "")
        rendered = rendered.replace("{{column_plus}}", f"+{column}" if column else "")
        rendered = rendered.replace("{{line_colon}}", f":{line}" if line else "")
        rendered = rendered.replace("{{column_colon}}", f":{column}" if column else "")
        rendered = rendered.replace("{{path_relative}}", path_rel)
        rendered = rendered.replace("{{path_name}}", path_name)
        rendered = rendered.replace("{{path}}", path_abs)
        rendered = rendered.replace("{{line}}", str(line) if line else "")
        rendered = rendered.replace("{{column}}", str(column) if column else "")

        # Split into command arguments using shlex to handle quotes and spaces
        return shlex.split(rendered)

    return builder
