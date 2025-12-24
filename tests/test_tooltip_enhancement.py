# Tests for tooltip enhancement with keyboard shortcuts


import pytest
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static

from textual_filelink import CommandLink, FileLink, ToggleableFileLink


class FileLinkTestApp(App):
    """Test app for FileLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def compose(self) -> ComposeResult:
        yield self.widget


class ToggleableFileLinkTestApp(App):
    """Test app for ToggleableFileLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def compose(self) -> ComposeResult:
        yield self.widget


class CommandLinkTestApp(App):
    """Test app for CommandLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def compose(self) -> ComposeResult:
        yield self.widget


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file


# ============================================================================
# FileLink Tooltip Enhancement Tests
# ============================================================================


async def test_filelink_tooltip_includes_shortcut(temp_file):
    """Test standalone FileLink tooltip includes keyboard shortcuts."""
    link = FileLink(temp_file)
    app = FileLinkTestApp(link)

    async with app.run_test():
        assert link.tooltip is not None
        assert "(enter/o)" in link.tooltip.lower()


async def test_filelink_embedded_no_tooltip(temp_file):
    """Test embedded FileLink doesn't get tooltip enhanced."""
    link = FileLink(temp_file, _embedded=True)
    app = FileLinkTestApp(link)

    async with app.run_test():
        # Embedded widgets shouldn't have tooltip set (since they're internal to parent)
        # Tooltip will be None since _embedded=True skips tooltip setting
        assert link.tooltip is None


async def test_filelink_custom_tooltip_enhanced(temp_file):
    """Test custom FileLink tooltip is enhanced with shortcut."""
    link = FileLink(temp_file, tooltip="My custom file")
    app = FileLinkTestApp(link)

    async with app.run_test():
        assert link.tooltip is not None
        assert "My custom file" in link.tooltip
        assert "(enter/o)" in link.tooltip.lower()


async def test_filelink_tooltip_format(temp_file):
    """Test FileLink tooltip format is 'description (keys)'."""
    link = FileLink(temp_file)
    app = FileLinkTestApp(link)

    async with app.run_test():
        # Should be in format "Open test.txt (enter/o)"
        assert link.tooltip.startswith("Open ")
        assert " (enter/o)" in link.tooltip


# ============================================================================
# ToggleableFileLink Tooltip Enhancement Tests
# ============================================================================


async def test_toggleable_toggle_tooltip_includes_shortcuts(temp_file):
    """Test toggle tooltip includes 'space' and 't' keys."""
    link = ToggleableFileLink(temp_file)
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        toggle_static = link.query_one("#toggle", Static)
        assert toggle_static.tooltip is not None
        assert "space" in toggle_static.tooltip.lower()
        assert "t" in toggle_static.tooltip.lower()
        # Should show both keys
        assert "/" in toggle_static.tooltip


async def test_toggleable_remove_tooltip_includes_shortcuts(temp_file):
    """Test remove tooltip includes 'x' and 'delete' keys."""
    link = ToggleableFileLink(temp_file)
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        remove_static = link.query_one("#remove", Static)
        assert remove_static.tooltip is not None
        assert "x" in remove_static.tooltip.lower()
        assert "delete" in remove_static.tooltip.lower()
        assert "/" in remove_static.tooltip


async def test_toggleable_clickable_icon_tooltip_includes_number(temp_file):
    """Test clickable icon tooltip includes number key."""
    link = ToggleableFileLink(
        temp_file,
        icons=[
            {"name": "star", "icon": "⭐", "clickable": True, "tooltip": "Favorite"},
        ],
    )
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        icon_static = link.query_one(".status-icon.clickable", Static)
        assert icon_static.tooltip is not None
        assert "Favorite" in icon_static.tooltip
        assert "(1)" in icon_static.tooltip


async def test_toggleable_multiple_icons_numbered_correctly(temp_file):
    """Test multiple clickable icons get correct number keys."""
    link = ToggleableFileLink(
        temp_file,
        icons=[
            {"name": "star", "icon": "⭐", "clickable": True, "tooltip": "Star"},
            {"name": "flag", "icon": "🚩", "clickable": True, "tooltip": "Flag"},
            {"name": "check", "icon": "✓", "clickable": False, "tooltip": "Check"},
        ],
    )
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        star_icon = link.query_one("#icon-star", Static)
        flag_icon = link.query_one("#icon-flag", Static)
        check_icon = link.query_one("#icon-check", Static)

        # Star and flag are clickable, so they get numbers
        assert "(1)" in star_icon.tooltip
        assert "(2)" in flag_icon.tooltip

        # Check is not clickable, so no number
        assert "(3)" not in check_icon.tooltip


async def test_toggleable_icon_without_tooltip_enhanced(temp_file):
    """Test clickable icon without explicit tooltip still gets enhanced."""
    link = ToggleableFileLink(
        temp_file,
        icons=[
            {"name": "star", "icon": "⭐", "clickable": True},  # No tooltip
        ],
    )
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        icon_static = link.query_one(".status-icon.clickable", Static)
        assert icon_static.tooltip is not None
        assert "(1)" in icon_static.tooltip


async def test_toggleable_dynamic_tooltip_update_enhances(temp_file):
    """Test dynamically updating tooltips still includes shortcuts."""
    link = ToggleableFileLink(temp_file, toggle_tooltip="Initial toggle")
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        # Update toggle tooltip dynamically
        link.set_toggle_tooltip("Custom toggle text")

        toggle_static = link.query_one("#toggle", Static)
        assert "Custom toggle text" in toggle_static.tooltip
        assert "space" in toggle_static.tooltip.lower()
        assert "t" in toggle_static.tooltip.lower()


async def test_toggleable_no_tooltip_generates_default_with_keys(temp_file):
    """Test that missing tooltip generates sensible default with keys."""
    link = ToggleableFileLink(temp_file, toggle_tooltip=None, remove_tooltip=None)
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        toggle_static = link.query_one("#toggle", Static)
        remove_static = link.query_one("#remove", Static)

        # Should have generated default + keys
        assert toggle_static.tooltip is not None
        assert "space" in toggle_static.tooltip.lower()

        assert remove_static.tooltip is not None
        assert "x" in remove_static.tooltip.lower()


# ============================================================================
# CommandLink Tooltip Enhancement Tests
# ============================================================================


async def test_commandlink_play_tooltip_includes_shortcuts(temp_file):
    """Test play button tooltip includes 'p' and 'space' keys."""
    link = CommandLink("Build", output_path=temp_file)
    app = CommandLinkTestApp(link)

    async with app.run_test():
        # Check play/stop button widget tooltip
        tooltip = link._play_stop_widget.tooltip
        assert tooltip is not None
        assert "p" in tooltip.lower()
        assert "space" in tooltip.lower()


async def test_commandlink_settings_tooltip_includes_shortcut(temp_file):
    """Test settings tooltip includes 's' key."""
    link = CommandLink("Build", output_path=temp_file, show_settings=True)
    app = CommandLinkTestApp(link)

    async with app.run_test():
        # Check settings widget tooltip
        tooltip = link._settings_widget.tooltip
        assert tooltip is not None
        assert "(s)" in tooltip.lower()


async def test_commandlink_stop_tooltip_includes_shortcuts(temp_file):
    """Test stop button tooltip includes shortcut keys."""
    link = CommandLink("Build", output_path=temp_file)
    app = CommandLinkTestApp(link)

    async with app.run_test():
        # Set to running state
        link.set_status(running=True)

        tooltip = link._play_stop_widget.tooltip
        assert tooltip is not None
        assert "Stop" in tooltip
        assert "p" in tooltip.lower()
        assert "space" in tooltip.lower()


async def test_commandlink_dynamic_tooltip_update_enhances(temp_file):
    """Test CommandLink dynamic status updates enhance tooltips."""
    link = CommandLink("Build", output_path=temp_file)
    app = CommandLinkTestApp(link)

    async with app.run_test():
        # Start running
        link.set_status(running=True)

        tooltip = link._play_stop_widget.tooltip
        assert tooltip is not None
        assert "Stop" in tooltip
        # Should have the p key in there (might be space/p or p/space depending on binding order)
        assert "p" in tooltip.lower()
        assert "space" in tooltip.lower()


# ============================================================================
# Custom Bindings Tests
# ============================================================================


async def test_custom_bindings_reflected_in_tooltip(temp_file):
    """Test that custom BINDINGS override is reflected in tooltips."""

    class CustomFileLink(FileLink):
        BINDINGS = [
            Binding("enter", "open_file", "Open", show=False),
        ]

    link = CustomFileLink(temp_file)
    app = FileLinkTestApp(link)

    async with app.run_test():
        assert link.tooltip is not None
        assert "(enter)" in link.tooltip.lower()
        assert "(o)" not in link.tooltip.lower()  # Original key not present


async def test_custom_bindings_multiple_keys(temp_file):
    """Test custom bindings with multiple keys bound to same action."""

    class CustomFileLink(FileLink):
        BINDINGS = [
            Binding("o", "open_file", "Open", show=False),
            Binding("enter", "open_file", "Open", show=False),
            Binding("ctrl+o", "open_file", "Open", show=False),
        ]

    link = CustomFileLink(temp_file)
    app = FileLinkTestApp(link)

    async with app.run_test():
        assert link.tooltip is not None
        # Should include all three keys
        assert "o" in link.tooltip.lower()
        assert "enter" in link.tooltip.lower()
        assert "ctrl+o" in link.tooltip.lower()


# ============================================================================
# Edge Cases Tests
# ============================================================================


async def test_icon_beyond_9th_position_no_key(temp_file):
    """Test icon beyond 9th position doesn't get number key."""
    icons = []
    for i in range(15):  # 15 clickable icons
        icons.append(
            {
                "name": f"icon_{i}",
                "icon": f"{i}",
                "clickable": True,
                "tooltip": f"Icon {i}",
            }
        )

    link = ToggleableFileLink(temp_file, icons=icons)
    app = ToggleableFileLinkTestApp(link)

    async with app.run_test():
        icon_9 = link.query_one("#icon-icon_8", Static)  # 9th clickable icon (0-indexed)
        icon_10 = link.query_one("#icon-icon_9", Static)  # 10th clickable icon

        # 9th should have (9)
        assert "(9)" in icon_9.tooltip

        # 10th should not have number key
        assert "(10)" not in icon_10.tooltip
        assert "Icon 9" in icon_10.tooltip


async def test_settings_icon_special_case(temp_file):
    """Test settings icon uses 's' key not a number."""
    link = CommandLink("Build", output_path=temp_file, show_settings=True)
    app = CommandLinkTestApp(link)

    async with app.run_test():
        tooltip = link._settings_widget.tooltip

        # Should use 's' key, not a number like (1)
        assert "(s)" in tooltip.lower()
        assert "Settings" in tooltip


async def test_tooltip_format_consistency(temp_file):
    """Test tooltip format is consistent across all widgets."""
    link1 = FileLink(temp_file)
    link2 = ToggleableFileLink(temp_file)
    link3 = CommandLink("Build", output_path=temp_file)

    app = FileLinkTestApp(link1)
    async with app.run_test():
        # FileLink should have tooltip with parentheses format
        assert "(" in link1.tooltip and ")" in link1.tooltip

        # Other widgets should exist
        assert link2 is not None
        assert link3 is not None
        # CommandLink tooltips are on child widgets
        assert "(" in link3._play_stop_widget.tooltip and ")" in link3._play_stop_widget.tooltip


async def test_empty_keys_returns_base_tooltip(temp_file):
    """Test that action with no keys returns base tooltip."""

    class NoBindingsLink(FileLink):
        BINDINGS = []  # No bindings

    link = NoBindingsLink(temp_file, tooltip="My tooltip")
    app = FileLinkTestApp(link)

    async with app.run_test():
        assert link.tooltip == "My tooltip"  # No enhancement since no bindings
