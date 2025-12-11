# tests/test_command_link.py
"""Tests for CommandLink widget."""
import logging

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from textual_filelink import CommandLink, FileLink

logging.getLogger("textual_filelink").setLevel(logging.DEBUG)

class CommandLinkTestApp(App):
    """Test app for CommandLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.play_clicked_events = []
        self.stop_clicked_events = []
        self.settings_clicked_events = []
        self.toggled_events = []
        self.removed_events = []
        self.file_clicked_events = []

    def compose(self) -> ComposeResult:
        yield self.widget

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        self.play_clicked_events.append(event)

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        self.stop_clicked_events.append(event)

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        self.settings_clicked_events.append(event)

    def on_toggleable_file_link_toggled(self, event):
        self.toggled_events.append(event)

    def on_toggleable_file_link_removed(self, event):
        self.removed_events.append(event)

    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.file_clicked_events.append(event)


@pytest.fixture
def temp_output_file(tmp_path):
    """Create a temporary output file for testing."""
    output_file = tmp_path / "output.log"
    output_file.write_text("command output")
    return output_file


class TestCommandLinkInitialization:
    """Test suite for CommandLink initialization."""

    def test_initialization_defaults(self):
        """Test CommandLink initializes with default values."""
        link = CommandLink("TestCommand")

        assert link.name == "TestCommand"
        assert link.output_path is None
        assert link.is_toggled is False

    def test_initialization_with_output_path(self, temp_output_file):
        """Test CommandLink initializes with output path."""
        link = CommandLink("TestCommand", output_path=temp_output_file)

        assert link.output_path == temp_output_file

    def test_initialization_with_toggle(self):
        """Test CommandLink initializes with toggle state."""
        link = CommandLink("TestCommand", initial_toggle=True)

        assert link.is_toggled is True

    def test_name_used_as_id(self):
        """Test command name is used as widget ID."""
        link = CommandLink("TestCommand")

        assert link.id == "TestCommand"

    async def test_has_all_required_icons(self):
        """Test CommandLink has status and play/stop icons."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Should have status icon
            status_icon = link.get_icon("status")
            assert status_icon is not None

            # Should have play/stop button
            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon is not None
            assert play_stop_icon["clickable"] is True

    async def test_settings_icon_visible_by_default(self):
        """Test settings icon is visible by default."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            settings_icon = link.get_icon("settings")
            assert settings_icon is not None
            assert settings_icon["visible"] is True

    async def test_settings_icon_hidden_when_disabled(self):
        """Test settings icon can be hidden."""
        link = CommandLink("TestCommand", show_settings=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            settings_icon = link.get_icon("settings")
            assert settings_icon is None


class TestCommandLinkPlayStop:
    """Test suite for play/stop functionality."""

    async def test_play_button_shown_when_not_running(self):
        """Test play button (▶) is shown when not running."""
        link = CommandLink("TestCommand", running=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "▶"

    async def test_stop_button_shown_when_running(self):
        """Test stop button (⏹) is shown when running."""
        link = CommandLink("TestCommand", running=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "⏹"

    async def test_stop_button_click_posts_event(self):
        """Test clicking stop button posts StopClicked event."""
        link = CommandLink("TestCommand", running=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#icon-play_stop")
            await pilot.pause()

            assert len(app.stop_clicked_events) == 1
            assert app.stop_clicked_events[0].name == "TestCommand"


class TestCommandLinkStatus:
    """Test suite for status icon and spinner functionality."""

    async def test_initial_status_icon(self):
        """Test initial status icon is set correctly."""
        link = CommandLink("TestCommand", initial_status_icon="✅")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            status_icon = link.get_icon("status")
            assert status_icon["icon"] == "✅"

    async def test_set_status_updates_icon(self):
        """Test set_status updates the status icon."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(icon="✅", tooltip="Success")
            await pilot.pause()

            status_icon = link.get_icon("status")
            assert status_icon["icon"] == "✅"
            assert status_icon["tooltip"] == "Success"

    async def test_set_status_running_shows_spinner(self):
        """Test set_status with running=True shows spinner."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(running=True, tooltip="Running...")
            await pilot.pause()

            # Spinner should be showing (status icon should be visible and animating)
            status_icon = link.get_icon("status")
            assert status_icon["visible"] is True
            # Icon should be one of the spinner frames
            assert status_icon["icon"] in CommandLink.SPINNER_FRAMES

    async def test_set_status_running_with_icon_overrides_spinner(self):
        """Test set_status with running=True and explicit icon shows icon, not spinner."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(icon="⏳", running=True, tooltip="Processing...")
            await pilot.pause()

            # Should show the explicit icon, not spinner
            status_icon = link.get_icon("status")
            assert status_icon["icon"] == "⏳"
            assert status_icon["visible"] is True

    async def test_set_status_not_running_stops_spinner(self):
        """Test set_status with running=False stops the spinner."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Start spinner
            link.set_status(running=True, tooltip="Running...")
            await pilot.pause()
            await asyncio.sleep(0.3)  # Let spinner animate

            # Stop it
            link.set_status(icon="✅", running=False, tooltip="Done")
            await pilot.pause()

            # Should show the status icon
            status_icon = link.get_icon("status")
            assert status_icon["icon"] == "✅"
            assert link.is_running is False

    async def test_set_status_updates_play_stop_button(self):
        """Test set_status updates the play/stop button."""
        link = CommandLink("TestCommand", running=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Start running
            link.set_status(running=True)
            await pilot.pause()

            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "⏹"
            assert link.is_running is True

            # Stop running
            link.set_status(running=False)
            await pilot.pause()

            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "▶"
            assert link.is_running is False

    async def test_spinner_cleans_up_on_unmount(self):
        """Test spinner timer is stopped when widget is unmounted."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(running=True)
            await pilot.pause()

            # Unmount the widget
            link.remove()
            await pilot.pause()

            # Timer should be stopped (no easy way to check directly,
            # but we verify it doesn't crash)
            assert link._spinner_timer is None or not link._spinner_timer.is_running


class TestCommandLinkOutputPath:
    """Test suite for output path functionality."""

    def test_set_output_path_updates_path(self, temp_output_file):
        """Test set_output_path updates the output path."""
        link = CommandLink("TestCommand", output_path=None)

        link.set_output_path(temp_output_file, tooltip="View output")

        assert link.output_path == temp_output_file

    async def test_set_output_path_updates_tooltip(self, temp_output_file):
        """Test set_output_path updates the file link tooltip."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_output_path(temp_output_file, tooltip="Click to view output")
            await pilot.pause()

            file_link = link.file_link
            assert file_link.tooltip == "Click to view output"

    async def test_clicking_output_opens_file(self, temp_output_file):
        """Test clicking command name opens output file when set."""
        link = CommandLink("TestCommand", output_path=temp_output_file)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Click the file link
            file_link = link.file_link
            await pilot.click(file_link)
            await pilot.pause()

            # Should post file clicked event
            assert len(app.file_clicked_events) == 1
            assert app.file_clicked_events[0].path == temp_output_file


class TestCommandLinkSettings:
    """Test suite for settings functionality."""

    async def test_settings_icon_click_posts_event(self):
        """Test clicking settings icon posts SettingsClicked event."""
        link = CommandLink("TestCommand", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#icon-settings")
            await pilot.pause()

            assert len(app.settings_clicked_events) == 1
            assert app.settings_clicked_events[0].name == "TestCommand"

    async def test_set_settings_tooltip(self):
        """Test set_settings_tooltip updates tooltip."""
        link = CommandLink("TestCommand", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_settings_tooltip("Configure test options")
            await pilot.pause()

            settings_icon = link.get_icon("settings")
            assert settings_icon["tooltip"] == "Configure test options"


class TestCommandLinkToggle:
    """Test suite for toggle functionality."""

    async def test_set_toggle_updates_state(self):
        """Test set_toggle updates the toggle state."""
        link = CommandLink("TestCommand", initial_toggle=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_toggle(True, tooltip="Selected")
            await pilot.pause()

            assert link.is_toggled is True

    async def test_set_toggle_updates_visual(self):
        """Test set_toggle updates the visual display."""
        link = CommandLink("TestCommand", initial_toggle=False, show_toggle=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_toggle(True)
            await pilot.pause()

            toggle_widget = link.query_one("#toggle", Static)
            # Content should be checked box
            assert "☑" in str(toggle_widget.render().plain)

    async def test_toggle_click_posts_event(self):
        """Test clicking toggle posts Toggled event."""
        link = CommandLink("TestCommand", show_toggle=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#toggle")
            await pilot.pause()

            assert len(app.toggled_events) == 1
            assert app.toggled_events[0].is_toggled is True


class TestCommandLinkRemove:
    """Test suite for remove functionality."""

    async def test_remove_button_click_posts_event(self):
        """Test clicking remove button posts Removed event."""
        link = CommandLink("TestCommand", show_remove=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#remove")
            await pilot.pause()

            assert len(app.removed_events) == 1

    async def test_remove_button_hidden_when_disabled(self):
        """Test remove button can be hidden."""
        link = CommandLink("TestCommand", show_remove=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Should not have remove button
            with pytest.raises(Exception):
                link.query_one("#remove")


class TestCommandLinkProperties:
    """Test suite for CommandLink properties."""

    def test_name_property(self):
        """Test name property returns command name."""
        link = CommandLink("TestCommand")
        assert link.name == "TestCommand"

    def test_output_path_property(self, temp_output_file):
        """Test output_path property returns current path."""
        link = CommandLink("TestCommand", output_path=temp_output_file)
        assert link.output_path == temp_output_file

    def test_is_running_property(self):
        """Test is_running property reflects running state."""
        link = CommandLink("TestCommand", running=True)
        assert link.is_running is True

        link2 = CommandLink("TestCommand2", running=False)
        assert link2.is_running is False

    def test_is_toggled_property(self):
        """Test is_toggled property reflects toggle state."""
        link = CommandLink("TestCommand", initial_toggle=True)
        assert link.is_toggled is True


class TestCommandLinkIntegration:
    """Integration tests for CommandLink."""

    async def test_complete_workflow(self, temp_output_file):
        """Test complete command workflow: start, run, complete."""
        link = CommandLink("TestCommand", initial_toggle=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Start command
            await pilot.click("#icon-play_stop")
            await pilot.pause()
            assert len(app.play_clicked_events) == 1

            # Simulate running
            link.set_status(running=True, tooltip="Running tests...")
            await pilot.pause()
            assert link.is_running is True

            # Simulate completion
            link.set_status(icon="✅", running=False, tooltip="Completed")
            link.set_output_path(temp_output_file, tooltip="View output")
            await pilot.pause()

            assert link.is_running is False
            assert link.output_path == temp_output_file

    async def test_all_features_combined(self, temp_output_file):
        """Test all CommandLink features working together."""
        link = CommandLink(
            "TestCommand",
            output_path=None,
            initial_toggle=True,
            initial_status_icon="❓",
            initial_status_tooltip="Not run",
            running=False,
            show_toggle=True,
            show_settings=True,
            show_remove=True,
        )
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Should start toggled
            assert link.is_toggled is True

            # Click play
            await pilot.click("#icon-play_stop")
            await pilot.pause()
            assert len(app.play_clicked_events) == 1

            # Update status
            link.set_status(running=True, tooltip="Running...")
            await pilot.pause()
            assert link.is_running is True

            # Click settings
            await pilot.click("#icon-settings")
            await pilot.pause()
            assert len(app.settings_clicked_events) == 1

            # Complete and set output
            link.set_status(icon="✅", running=False, tooltip="Done")
            link.set_output_path(temp_output_file, tooltip="View output")
            await pilot.pause()

            # Toggle off
            await pilot.click("#toggle")
            await pilot.pause()
            assert link.is_toggled is False

            # Remove
            await pilot.click("#remove")
            await pilot.pause()
            assert len(app.removed_events) == 1


# Import asyncio for spinner tests
import asyncio
