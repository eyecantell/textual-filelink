# Updated test_toggleable_file_link.py with multi-icon support

import pytest
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Static

from textual_filelink import FileLink, ToggleableFileLink
from textual_filelink.toggleable_file_link import IconConfig


class ToggleableFileLinkTestApp(App):
    """Test app for ToggleableFileLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.toggled_events = []
        self.removed_events = []
        self.clicked_events = []
        self.icon_clicked_events = []

    def compose(self) -> ComposeResult:
        yield self.widget

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.toggled_events.append(event)

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.removed_events.append(event)

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        self.icon_clicked_events.append(event)

    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.clicked_events.append(event)


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    return test_file


class TestToggleableFileLink:
    """Test suite for ToggleableFileLink widget."""

    async def test_initialization_default(self, temp_file):
        """Test ToggleableFileLink initializes with default values."""
        link = ToggleableFileLink(temp_file)

        assert link.path == temp_file
        assert link.is_toggled is False
        assert len(link.icons) == 0

    async def test_initialization_with_toggle(self, temp_file):
        """Test ToggleableFileLink initializes with toggle state."""
        link = ToggleableFileLink(temp_file, initial_toggle=True)

        assert link.is_toggled is True

    async def test_toggle_click_changes_state(self, temp_file):
        """Test clicking toggle changes state."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            assert link.is_toggled is False

            await pilot.click("#toggle")
            await pilot.pause()

            assert link.is_toggled is True
            assert len(app.toggled_events) == 1
            assert app.toggled_events[0].is_toggled is True

    async def test_toggle_click_twice(self, temp_file):
        """Test clicking toggle twice returns to original state."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#toggle")
            await pilot.pause()
            await pilot.click("#toggle")
            await pilot.pause()

            assert link.is_toggled is False
            assert len(app.toggled_events) == 2
            assert app.toggled_events[0].is_toggled is True
            assert app.toggled_events[1].is_toggled is False

    async def test_toggle_visual_update(self, temp_file, get_rendered_text):
        """Test toggle visual updates correctly."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            toggle_widget = link.query_one("#toggle", Static)
            assert get_rendered_text(toggle_widget) == "☐"

            await pilot.click("#toggle")
            await pilot.pause()

            assert get_rendered_text(toggle_widget) == "☑"

    async def test_remove_click_posts_message(self, temp_file):
        """Test clicking remove button posts Removed message."""
        link = ToggleableFileLink(temp_file, show_remove=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#remove")
            await pilot.pause()

            assert len(app.removed_events) == 1
            assert app.removed_events[0].path == temp_file

    async def test_toggle_only_layout(self, temp_file):
        """Test layout with toggle only (no remove)."""
        link = ToggleableFileLink(temp_file, show_toggle=True, show_remove=False)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # Should have toggle
            assert link.query_one("#toggle", Static)

            # Should not have remove
            with pytest.raises(NoMatches):
                link.query_one("#remove", Static)

    async def test_remove_only_layout(self, temp_file):
        """Test layout with remove only (no toggle)."""
        link = ToggleableFileLink(temp_file, show_toggle=False, show_remove=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # Should not have toggle
            with pytest.raises(NoMatches):
                link.query_one("#toggle", Static)

            # Should have remove
            assert link.query_one("#remove", Static)

    async def test_no_controls_layout(self, temp_file):
        """Test layout with no controls."""
        link = ToggleableFileLink(temp_file, show_toggle=False, show_remove=False)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # Should not have toggle or remove
            with pytest.raises(NoMatches):
                link.query_one("#toggle", Static)
            with pytest.raises(NoMatches):
                link.query_one("#remove", Static)

    async def test_disable_on_untoggle(self, temp_file):
        """Test disable_on_untoggle adds disabled class."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, disable_on_untoggle=True, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # Should start disabled
            assert "disabled" in link.classes

            # Toggle on
            await pilot.click("#toggle")
            await pilot.pause()

            # Should no longer be disabled
            assert "disabled" not in link.classes

            # Toggle off
            await pilot.click("#toggle")
            await pilot.pause()

            # Should be disabled again
            assert "disabled" in link.classes

    async def test_file_link_click_bubbles(self, temp_file):
        """Test FileLink click events bubble up from ToggleableFileLink."""
        link = ToggleableFileLink(temp_file, line=10, column=5)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # Click on the FileLink component
            file_link = link.query_one(FileLink)
            await pilot.click(file_link)
            await pilot.pause()

            assert len(app.clicked_events) == 1
            event = app.clicked_events[0]
            assert event.path == temp_file
            assert event.line == 10
            assert event.column == 5

    async def test_file_link_click_blocked_when_disabled(self, temp_file):
        """Test FileLink click is blocked when disable_on_untoggle is active."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, disable_on_untoggle=True, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # Try to click FileLink while disabled
            await pilot.click(FileLink)
            await pilot.pause()

            # Click should be blocked
            assert len(app.clicked_events) == 0

            # Toggle on
            await pilot.click("#toggle")
            await pilot.pause()

            # Now click should work
            await pilot.click(FileLink)
            await pilot.pause()

            assert len(app.clicked_events) == 1

    async def test_command_builder_passed_to_filelink(self, temp_file):
        """Test command_builder is passed to internal FileLink."""

        def custom_builder(path, line, column):
            return ["custom", str(path)]

        link = ToggleableFileLink(temp_file, command_builder=custom_builder)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            file_link = link.query_one(FileLink)
            assert file_link._command_builder == custom_builder

    async def test_line_and_column_passed_to_filelink(self, temp_file):
        """Test line and column are passed to internal FileLink."""
        link = ToggleableFileLink(temp_file, line=42, column=7)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            file_link = link.query_one(FileLink)
            assert file_link.line == 42
            assert file_link.column == 7

    async def test_path_property(self, temp_file):
        """Test path property returns correct path."""
        link = ToggleableFileLink(temp_file)

        assert link.path == temp_file

    async def test_is_toggled_property(self, temp_file):
        """Test is_toggled property reflects current state."""
        link = ToggleableFileLink(temp_file, initial_toggle=True)

        assert link.is_toggled is True


class TestMultipleIcons:
    """Test suite for multiple icon functionality."""

    async def test_single_icon_dict(self, temp_file):
        """Test creating link with single icon as dict."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓"}])

        assert len(link.icons) == 1
        assert link.icons[0]["name"] == "status"
        assert link.icons[0]["icon"] == "✓"

    async def test_single_icon_dataclass(self, temp_file):
        """Test creating link with single icon as IconConfig."""
        icon_config = IconConfig(name="status", icon="✓")
        link = ToggleableFileLink(temp_file, icons=[icon_config])

        assert len(link.icons) == 1
        assert link.icons[0]["name"] == "status"

    async def test_multiple_icons(self, temp_file):
        """Test creating link with multiple icons."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "status", "icon": "✓"},
                {"name": "warning", "icon": "⚠"},
                {"name": "lock", "icon": "🔒"},
            ],
        )

        assert len(link.icons) == 3
        assert link.icons[0]["name"] == "status"
        assert link.icons[1]["name"] == "warning"
        assert link.icons[2]["name"] == "lock"

    async def test_icons_before_position(self, temp_file, get_rendered_text):
        """Test icons with 'before' position appear before filename."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "icon1", "icon": "🔥", "position": "before"},
                {"name": "icon2", "icon": "⭐", "position": "before"},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # Both icons should be present
            icon1 = link.query_one("#icon-icon1", Static)
            icon2 = link.query_one("#icon-icon2", Static)
            assert get_rendered_text(icon1) == "🔥"
            assert get_rendered_text(icon2) == "⭐"

    async def test_icons_after_position(self, temp_file, get_rendered_text):
        """Test icons with 'after' position appear after filename."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "icon1", "icon": "🔥", "position": "after"},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            icon1 = link.query_one("#icon-icon1", Static)
            assert get_rendered_text(icon1) == "🔥"

    async def test_icons_mixed_positions(self, temp_file):
        """Test icons with mixed positions."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "before1", "icon": "🔥", "position": "before"},
                {"name": "after1", "icon": "⭐", "position": "after"},
                {"name": "before2", "icon": "✓", "position": "before"},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # All icons should be present
            assert link.query_one("#icon-before1", Static)
            assert link.query_one("#icon-before2", Static)
            assert link.query_one("#icon-after1", Static)

    async def test_icon_visibility(self, temp_file):
        """Test icon visibility control."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "visible", "icon": "✓", "visible": True},
                {"name": "hidden", "icon": "⚠", "visible": False},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            # Visible icon should exist
            visible_icon = link.query_one("#icon-visible", Static)
            assert visible_icon.display is True

            # Hidden icon should not be rendered
            with pytest.raises(NoMatches):
                link.query_one("#icon-hidden", Static)

    async def test_icon_clickable(self, temp_file):
        """Test clickable icons post events."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "clickable", "icon": "✓", "clickable": True},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#icon-clickable")
            await pilot.pause()

            assert len(app.icon_clicked_events) == 1
            event = app.icon_clicked_events[0]
            assert event.icon_name == "clickable"
            assert event.icon == "✓"

    async def test_icon_not_clickable(self, temp_file):
        """Test non-clickable icons don't post events."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "not_clickable", "icon": "✓", "clickable": False},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#icon-not_clickable")
            await pilot.pause()

            # Should not post event
            assert len(app.icon_clicked_events) == 0

    async def test_icon_tooltip(self, temp_file):
        """Test icon tooltips are set correctly."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "status", "icon": "✓", "tooltip": "All good!"},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            icon = link.query_one("#icon-status", Static)
            assert icon.tooltip == "All good!"

    async def test_icon_ordering_by_index(self, temp_file):
        """Test icons are ordered by explicit index."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "third", "icon": "3", "index": 3},
                {"name": "first", "icon": "1", "index": 1},
                {"name": "second", "icon": "2", "index": 2},
            ],
        )

        # Icons should be sorted by index
        sorted_icons = link._sort_icons(link._icons, "before")
        assert sorted_icons[0].name == "first"
        assert sorted_icons[1].name == "second"
        assert sorted_icons[2].name == "third"

    async def test_icon_ordering_by_list_position(self, temp_file):
        """Test icons without index maintain list order."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "first", "icon": "1"},
                {"name": "second", "icon": "2"},
                {"name": "third", "icon": "3"},
            ],
        )

        sorted_icons = link._sort_icons(link._icons, "before")
        assert sorted_icons[0].name == "first"
        assert sorted_icons[1].name == "second"
        assert sorted_icons[2].name == "third"

    async def test_icon_ordering_mixed_index_and_auto(self, temp_file):
        """Test icons with mixed explicit and auto indices."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "auto1", "icon": "A"},
                {"name": "explicit", "icon": "E", "index": 0},
                {"name": "auto2", "icon": "B"},
            ],
        )

        # Explicit index should come first
        sorted_icons = link._sort_icons(link._icons, "before")
        assert sorted_icons[0].name == "explicit"
        assert sorted_icons[1].name == "auto1"
        assert sorted_icons[2].name == "auto2"

    async def test_icon_ordering_duplicate_index(self, temp_file):
        """Test icons with duplicate indices are ordered by name."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "zebra", "icon": "Z", "index": 1},
                {"name": "apple", "icon": "A", "index": 1},
            ],
        )

        sorted_icons = link._sort_icons(link._icons, "before")
        assert sorted_icons[0].name == "apple"  # Alphabetically first
        assert sorted_icons[1].name == "zebra"


class TestIconManipulation:
    """Test suite for dynamic icon manipulation."""

    async def test_set_icon_visible(self, temp_file):
        """Test showing/hiding icons dynamically."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "visible": True}])
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # Hide the icon
            link.set_icon_visible("status", False)
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["visible"] is False

            # Show it again
            link.set_icon_visible("status", True)
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["visible"] is True

    async def test_set_icon_visible_nonexistent(self, temp_file):
        """Test setting visibility of nonexistent icon raises KeyError."""
        link = ToggleableFileLink(temp_file, icons=[])

        with pytest.raises(KeyError):
            link.set_icon_visible("nonexistent", True)

    async def test_update_icon_properties(self, temp_file):
        """Test updating icon properties."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "⏳", "tooltip": "Processing"}])
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # Update icon and tooltip
            link.update_icon("status", icon="✓", tooltip="Complete")
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["icon"] == "✓"
            assert icon_config["tooltip"] == "Complete"

    async def test_update_icon_visibility(self, temp_file):
        """Test updating icon visibility via update_icon."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "visible": True}])
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            link.update_icon("status", visible=False)
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["visible"] is False

    async def test_update_icon_clickable(self, temp_file):
        """Test updating icon clickable state."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "clickable": False}])
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            link.update_icon("status", clickable=True)
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["clickable"] is True

    async def test_update_icon_position(self, temp_file):
        """Test updating icon position triggers recompose."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "position": "before"}])
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            link.update_icon("status", position="after")
            await pilot.pause()

            icon_config = link.get_icon("status")
            assert icon_config["position"] == "after"

    async def test_update_icon_index(self, temp_file):
        """Test updating icon index triggers recompose."""
        link = ToggleableFileLink(
            temp_file,
            icons=[
                {"name": "first", "icon": "1"},
                {"name": "second", "icon": "2"},
            ],
        )
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            link.update_icon("second", index=0)
            await pilot.pause()

            icon_config = link.get_icon("second")
            assert icon_config["index"] == 0

    async def test_update_icon_nonexistent(self, temp_file):
        """Test updating nonexistent icon raises KeyError."""
        link = ToggleableFileLink(temp_file, icons=[])

        with pytest.raises(KeyError):
            link.update_icon("nonexistent", icon="✓")

    async def test_update_icon_invalid_property(self, temp_file):
        """Test updating invalid property raises ValueError."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓"}])

        with pytest.raises(ValueError):
            link.update_icon("status", invalid_prop="value")

    async def test_update_icon_invalid_position(self, temp_file):
        """Test updating to invalid position raises ValueError."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓"}])

        with pytest.raises(ValueError):
            link.update_icon("status", position="middle")

    async def test_get_icon(self, temp_file):
        """Test getting icon configuration."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "tooltip": "Done"}])

        icon_config = link.get_icon("status")
        assert icon_config is not None
        assert icon_config["name"] == "status"
        assert icon_config["icon"] == "✓"
        assert icon_config["tooltip"] == "Done"

    async def test_get_icon_returns_copy(self, temp_file):
        """Test get_icon returns a copy, not reference."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓"}])

        icon_config = link.get_icon("status")
        icon_config["icon"] = "⚠"  # Modify copy

        # Original should be unchanged
        original = link.get_icon("status")
        assert original["icon"] == "✓"

    async def test_get_icon_nonexistent(self, temp_file):
        """Test getting nonexistent icon returns None."""
        link = ToggleableFileLink(temp_file, icons=[])

        icon_config = link.get_icon("nonexistent")
        assert icon_config is None


class TestBackwardsCompatibility:
    """Test suite for backwards compatibility with old status_icon API."""

    async def test_status_icon_deprecated(self, temp_file):
        """Test old status_icon parameter shows deprecation warning."""
        with pytest.warns(DeprecationWarning):
            link = ToggleableFileLink(temp_file, status_icon="✓")

        # Should still work
        assert len(link.icons) == 1
        assert link.icons[0]["name"] == "status"
        assert link.icons[0]["icon"] == "✓"

    async def test_status_icon_clickable_deprecated(self, temp_file):
        """Test old status_icon_clickable parameter works."""
        with pytest.warns(DeprecationWarning):
            link = ToggleableFileLink(temp_file, status_icon="✓", status_icon_clickable=True)

        assert link.icons[0]["clickable"] is True

    async def test_status_tooltip_deprecated(self, temp_file):
        """Test old status_tooltip parameter works."""
        with pytest.warns(DeprecationWarning):
            link = ToggleableFileLink(temp_file, status_icon="✓", status_tooltip="All good")

        assert link.icons[0]["tooltip"] == "All good"

    async def test_status_icon_with_icons_parameter(self, temp_file):
        """Test status_icon is added to icons list."""
        with pytest.warns(DeprecationWarning):
            link = ToggleableFileLink(temp_file, status_icon="✓", icons=[{"name": "other", "icon": "⚠"}])

        assert len(link.icons) == 2
        # Status icon should be added
        names = [ic["name"] for ic in link.icons]
        assert "status" in names
        assert "other" in names


class TestValidation:
    """Test suite for icon validation."""

    def test_missing_name_raises_error(self, temp_file):
        """Test icon without name raises ValueError."""
        with pytest.raises(ValueError, match="missing required field 'name'"):
            ToggleableFileLink(temp_file, icons=[{"icon": "✓"}])

    def test_missing_icon_raises_error(self, temp_file):
        """Test icon without icon raises ValueError."""
        with pytest.raises(ValueError, match="missing required field 'icon'"):
            ToggleableFileLink(temp_file, icons=[{"name": "status"}])

    def test_duplicate_names_raises_error(self, temp_file):
        """Test duplicate icon names raise ValueError."""
        with pytest.raises(ValueError, match="Duplicate icon name"):
            ToggleableFileLink(
                temp_file,
                icons=[
                    {"name": "status", "icon": "✓"},
                    {"name": "status", "icon": "⚠"},
                ],
            )

    def test_invalid_position_raises_error(self, temp_file):
        """Test invalid position raises ValueError."""
        with pytest.raises(ValueError, match="invalid position"):
            ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "position": "middle"}])

    def test_invalid_icon_type_raises_error(self, temp_file):
        """Test invalid icon type raises ValueError."""
        with pytest.raises(ValueError, match="must be IconConfig or dict"):
            ToggleableFileLink(temp_file, icons=["not a dict"])

    async def test_toggle_tooltip_applied(self, temp_file):
        """Test toggle tooltip is properly applied."""
        link = ToggleableFileLink(temp_file, toggle_tooltip="Click to toggle")
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            toggle = link.query_one("#toggle", expect_type=Static)
            assert toggle.tooltip == "Click to toggle"

    async def test_remove_tooltip_applied(self, temp_file):
        """Test remove tooltip is properly applied."""
        link = ToggleableFileLink(temp_file, remove_tooltip="Click to remove")
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test():
            remove = link.query_one("#remove", expect_type=Static)
            assert remove.tooltip == "Click to remove"

    async def test_icon_clickable_toggle(self, temp_file):
        """Test toggling icon clickable state."""
        link = ToggleableFileLink(temp_file, icons=[{"name": "status", "icon": "✓", "clickable": False}])

        # Icon should exist and not be clickable initially
        icon = link.get_icon("status")
        assert icon is not None
        assert icon["clickable"] is False

        # Update to clickable
        link.update_icon("status", clickable=True)

        # Verify the change was applied
        icon_updated = link.get_icon("status")
        assert icon_updated["clickable"] is True

    # === Keyboard Accessibility Tests ===

    async def test_toggleable_filelink_can_focus(self, temp_file):
        """Test that ToggleableFileLink is focusable."""
        link = ToggleableFileLink(temp_file)

        assert link.can_focus is True

    async def test_toggleable_filelink_receives_focus(self, temp_file):
        """Test that ToggleableFileLink can receive focus via Tab."""
        link = ToggleableFileLink(temp_file)
        app = ToggleableFileLinkTestApp(link)

        async with app.run_test() as pilot:
            # ToggleableFileLink should be focusable
            assert link.can_focus is True

            # Tab to navigate (could focus internal FileLink or other components)
            await pilot.press("tab")
            await pilot.pause()

            # Some widget should be focused
            assert app.focused is not None

    async def test_toggleable_filelink_focus_multiple_widgets(self, temp_file):
        """Test that multiple ToggleableFileLink widgets are all focusable."""

        class MultipleToggleableApp(App):
            def compose(self) -> ComposeResult:
                yield ToggleableFileLink(temp_file, id="link1")
                yield ToggleableFileLink(temp_file, id="link2")

        app = MultipleToggleableApp()
        async with app.run_test() as pilot:
            # Get both links
            link1 = app.query_one("#link1", ToggleableFileLink)
            link2 = app.query_one("#link2", ToggleableFileLink)

            # Both should be focusable
            assert link1.can_focus is True
            assert link2.can_focus is True

            # Tab navigation should work (we can't easily test which widget is focused
            # due to Textual's internal focus handling, but we can verify they're focusable)
            await pilot.press("tab")
            await pilot.pause()

            # At least one widget should be focused
            assert app.focused is not None
