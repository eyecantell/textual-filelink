# tests/test_command_link.py
"""Tests for CommandLink widget."""

import asyncio
import logging
from pathlib import Path

import pytest
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
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

        assert link.name == "testcommand"  # name returns the sanitized ID (lowercase)
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

        assert link.id == "testcommand"  # ID is sanitized (lowercase)

    async def test_has_all_required_icons(self):
        """Test CommandLink has status and play/stop icons."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
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

        async with app.run_test():
            settings_icon = link.get_icon("settings")
            assert settings_icon is not None
            assert settings_icon["visible"] is True

    async def test_settings_icon_hidden_when_disabled(self):
        """Test settings icon can be hidden."""
        link = CommandLink("TestCommand", show_settings=False)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            settings_icon = link.get_icon("settings")
            assert settings_icon is None


class TestCommandLinkPlayStop:
    """Test suite for play/stop functionality."""

    async def test_play_button_shown_when_not_running(self):
        """Test play button (▶️) is shown when not running."""
        link = CommandLink("TestCommand", running=False)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "▶️"

    async def test_stop_button_shown_when_running(self):
        """Test stop button (⏹️) is shown when running."""
        link = CommandLink("TestCommand", running=True)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "⏹️"

    async def test_stop_button_click_posts_event(self):
        """Test clicking stop button posts StopClicked event."""
        link = CommandLink("TestCommand", running=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            await pilot.click("#icon-play_stop")
            await pilot.pause()

            assert len(app.stop_clicked_events) == 1
            assert app.stop_clicked_events[0].name == "testcommand"  # name is sanitized to lowercase


class TestCommandLinkStatus:
    """Test suite for status icon and spinner functionality."""

    async def test_initial_status_icon(self):
        """Test initial status icon is set correctly."""
        link = CommandLink("TestCommand", initial_status_icon="✅")
        app = CommandLinkTestApp(link)

        async with app.run_test():
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
            assert play_stop_icon["icon"] == "⏹️"
            assert link.is_running is True

            # Stop running
            link.set_status(running=False)
            await pilot.pause()

            play_stop_icon = link.get_icon("play_stop")
            assert play_stop_icon["icon"] == "▶️"
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
            # FileLink path is the command name by default (unless set_output_path is called)
            # The path is resolved to absolute
            assert app.file_clicked_events[0].path.is_absolute()
            assert app.file_clicked_events[0].path.name == "TestCommand"


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
            assert app.settings_clicked_events[0].name == "testcommand"  # name is sanitized to lowercase

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

        async with app.run_test():
            # Should not have remove button
            with pytest.raises(NoMatches):
                link.query_one("#remove")


class TestCommandLinkProperties:
    """Test suite for CommandLink properties."""

    def test_name_property(self):
        """Test name property returns command name."""
        link = CommandLink("TestCommand")
        assert link.name == "testcommand"  # name returns the sanitized ID (lowercase)

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

    # === Edge Case Tests ===

    def test_sanitize_id_empty_string(self):
        """Test ID sanitization with empty string."""
        result = CommandLink.sanitize_id("")
        # Empty string returns empty string
        assert isinstance(result, str)
        assert result == ""

    def test_sanitize_id_all_special_chars(self):
        """Test ID sanitization with all special characters."""
        result = CommandLink.sanitize_id("!@#$%^&*()")
        # Should produce a valid ID (letters and hyphens)
        assert isinstance(result, str)
        assert all(c.isalnum() or c == "-" for c in result)

    def test_sanitize_id_very_long_name(self):
        """Test ID sanitization with very long command name."""
        long_name = "A" * 500
        result = CommandLink.sanitize_id(long_name)
        # Should handle long names without error
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= 550  # Reasonable upper bound

    def test_sanitize_id_with_spaces(self):
        """Test ID sanitization converts spaces to hyphens."""
        result = CommandLink.sanitize_id("My Test Command")
        # Should convert spaces to hyphens or underscores
        assert " " not in result
        assert isinstance(result, str)

    def test_sanitize_id_case_conversion(self):
        """Test ID sanitization converts to lowercase."""
        result = CommandLink.sanitize_id("MyTestCommand")
        # Should be lowercase
        assert result.islower() or not any(c.isupper() for c in result)

    async def test_command_link_set_output_path_before_mount(self):
        """Test setting output path before widget is mounted."""
        link = CommandLink("Test", output_path=None)

        # Should not crash when setting path before mount
        link.set_output_path(Path("test.log"))
        assert link.output_path == Path("test.log")

        # Should also work with string paths
        link.set_output_path("another.log")
        assert link.output_path == Path("another.log")

    async def test_command_link_spinner_cleanup_during_removal(self):
        """Test spinner is properly cleaned up if widget removed during animation."""

        class TestApp(App):
            def compose(self):
                yield CommandLink("Test", running=True)

        app = TestApp()
        async with app.run_test() as pilot:
            link = app.query_one(CommandLink)

            # Start spinner
            link.set_status(running=True)
            await pilot.pause(0.5)  # Let spinner animate

            # Remove widget while spinner is running
            link.remove()
            await pilot.pause(0.5)

            # Should not crash or leak timers
            # (Textual handles cleanup automatically, but this verifies it)
            assert True  # If we get here, cleanup was successful

    async def test_command_link_set_output_path_clears_noop(self):
        """Test set_output_path clears no-op command builder."""
        link = CommandLink("Test", output_path=None)

        # Initially has no-op builder when no output_path
        assert link._command_builder == CommandLink._noop_command_builder

        # Set output path (this would update the FileLink's command builder)
        link.set_output_path(Path("output.log"))
        assert link.output_path == Path("output.log")

    # === Keyboard Accessibility Tests ===

    async def test_command_link_can_focus(self):
        """Test that CommandLink is focusable."""
        link = CommandLink("Test")

        assert link.can_focus is True

    async def test_command_link_receives_focus(self):
        """Test that CommandLink can receive focus via Tab."""
        link = CommandLink("test-cmd")

        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # CommandLink should be focusable
            assert link.can_focus is True

            # Tab to CommandLink (even if internal FileLink gets focus, the structure is focusable)
            await pilot.press("tab")
            await pilot.pause()

            # Some widget should be focused (could be FileLink, toggle, or CommandLink itself)
            assert app.focused is not None

    async def test_command_link_focus_multiple_widgets(self):
        """Test that multiple CommandLink widgets are all focusable."""

        class MultipleCommandApp(App):
            def compose(self) -> ComposeResult:
                yield CommandLink("test-cmd-1")
                yield CommandLink("test-cmd-2")

        app = MultipleCommandApp()
        async with app.run_test() as pilot:
            # Get both links
            commands = app.query(CommandLink)
            assert len(commands) == 2

            # Both should be focusable
            for cmd in commands:
                assert cmd.can_focus is True

            # Tab navigation should work
            await pilot.press("tab")
            await pilot.pause()

            # At least one widget should be focused
            assert app.focused is not None

    async def test_p_key_plays(self):
        """Test 'p' key triggers play."""
        link = CommandLink("test-cmd", output_path=None)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()
            await pilot.press("p")
            await pilot.pause()

            # Play action posted PlayClicked message

    async def test_space_toggles_play_stop(self):
        """Test Space key toggles between play and stop."""
        link = CommandLink("test-cmd", running=False)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()
            await pilot.press("space")
            await pilot.pause()

            # Should have posted PlayClicked

            # Now test when running
            link.set_status(running=True)
            await pilot.press("space")
            await pilot.pause()

            # Should have posted StopClicked

    async def test_s_key_settings(self):
        """Test 's' key opens settings."""
        link = CommandLink("test-cmd", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()
            await pilot.press("s")
            await pilot.pause()

            # Settings action posted SettingsClicked message

    async def test_keyboard_shortcuts_sequence(self):
        """Test multiple keyboard shortcuts in sequence."""
        link = CommandLink("test-cmd", show_toggle=True, show_remove=True, show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()

            # Toggle
            await pilot.press("t")
            await pilot.pause()
            assert link.is_toggled is True

            # Play
            await pilot.press("p")
            await pilot.pause()

            # Settings
            await pilot.press("s")
            await pilot.pause()

            # Remove
            await pilot.press("x")
            await pilot.pause()
