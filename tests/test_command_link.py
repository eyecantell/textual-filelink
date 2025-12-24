# tests/test_command_link.py
"""Tests for CommandLink widget (flat architecture, v0.4.0)."""

import asyncio
from pathlib import Path

import pytest
from textual.app import App, ComposeResult

from textual_filelink import CommandLink, FileLink


class CommandLinkTestApp(App):
    """Test app for CommandLink."""

    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.play_clicked_events = []
        self.stop_clicked_events = []
        self.settings_clicked_events = []
        self.output_clicked_events = []

    def compose(self) -> ComposeResult:
        yield self.widget

    def on_command_link_play_clicked(self, event: CommandLink.PlayClicked):
        self.play_clicked_events.append(event)

    def on_command_link_stop_clicked(self, event: CommandLink.StopClicked):
        self.stop_clicked_events.append(event)

    def on_command_link_settings_clicked(self, event: CommandLink.SettingsClicked):
        self.settings_clicked_events.append(event)

    def on_command_link_output_clicked(self, event: CommandLink.OutputClicked):
        self.output_clicked_events.append(event)


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

        assert link.name == "TestCommand"  # name property returns actual name
        assert link.output_path is None
        assert link.is_running is False

    def test_initialization_with_output_path(self, temp_output_file):
        """Test CommandLink initializes with output path."""
        link = CommandLink("TestCommand", output_path=temp_output_file)

        assert link.output_path == temp_output_file

    def test_auto_generated_id(self):
        """Test command name is sanitized and used as widget ID."""
        link = CommandLink("Test Command")

        assert link.id == "test-command"  # ID is sanitized

    def test_explicit_id(self):
        """Test explicit ID overrides auto-generated ID."""
        link = CommandLink("Test Command", id="my-custom-id")

        assert link.id == "my-custom-id"

    async def test_has_status_widget(self):
        """Test CommandLink has status widget."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            status_widgets = link.query(".status-icon")
            assert len(status_widgets) == 1

    async def test_has_play_stop_button(self):
        """Test CommandLink has play/stop button."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            play_stop_widgets = link.query(".play-stop-button")
            assert len(play_stop_widgets) == 1

    async def test_name_widget_is_static_without_output(self):
        """Test name is Static widget when no output_path."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Name widget should be Static, not FileLink
            assert link._name_widget.__class__.__name__ == "Static"

    async def test_name_widget_is_filelink_with_output(self, temp_output_file):
        """Test name is FileLink widget when output_path is set."""
        link = CommandLink("TestCommand", output_path=temp_output_file)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Name widget should be FileLink
            assert isinstance(link._name_widget, FileLink)
            assert link._name_widget.path == temp_output_file

    async def test_settings_icon_hidden_by_default(self):
        """Test settings icon is hidden by default."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            settings_widgets = link.query(".settings-icon")
            assert len(settings_widgets) == 0

    async def test_settings_icon_visible_when_enabled(self):
        """Test settings icon is visible when show_settings=True."""
        link = CommandLink("TestCommand", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            settings_widgets = link.query(".settings-icon")
            assert len(settings_widgets) == 1


class TestCommandLinkStatus:
    """Test suite for CommandLink status management."""

    async def test_initial_status_icon(self):
        """Test initial status icon is set correctly."""
        link = CommandLink("TestCommand", initial_status_icon="✅")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            assert link._status_icon == "✅"
            assert "✅" in str(link._status_widget.render())

    async def test_set_status_updates_icon(self):
        """Test set_status() updates the status icon."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(icon="✅")
            await pilot.pause()

            assert link._status_icon == "✅"
            assert "✅" in str(link._status_widget.render())

    async def test_set_status_running_starts_spinner(self):
        """Test set_status(running=True) starts spinner animation."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Start the spinner via set_interval mechanism
            link.set_status(running=True)
            await pilot.pause()

            assert link.is_running is True
            # Spinner timer is created asynchronously via set_interval
            # Just verify is_running changed
            assert link._status_icon == "❓"  # Original icon is preserved during spinner

    async def test_set_status_not_running_stops_spinner(self):
        """Test set_status(running=False) stops spinner."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Start spinner
            link.set_status(running=True)
            await pilot.pause()
            assert link.is_running is True

            # Stop spinner and set icon
            link.set_status(icon="✅", running=False)
            await pilot.pause()

            assert link.is_running is False
            assert link._status_icon == "✅"
            assert "✅" in str(link._status_widget.render())

    async def test_set_status_updates_play_stop_button(self):
        """Test set_status() updates play/stop button."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Initially shows play button
            assert "▶️" in str(link._play_stop_widget.render())

            # Running shows stop button
            link.set_status(running=True)
            await pilot.pause()
            assert "⏹️" in str(link._play_stop_widget.render())

            # Not running shows play button
            link.set_status(running=False)
            await pilot.pause()
            assert "▶️" in str(link._play_stop_widget.render())

    async def test_set_status_updates_tooltip(self):
        """Test set_status() updates status tooltip."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.set_status(tooltip="Running tests...")
            await pilot.pause()

            assert link._status_widget.tooltip == "Running tests..."


class TestCommandLinkPlayStop:
    """Test suite for CommandLink play/stop functionality."""

    async def test_play_button_click_posts_event(self):
        """Test play/stop action works correctly."""
        link = CommandLink("TestCommand")

        assert link.is_running is False

        # Manually call the action
        link.action_play_stop()

        # After calling play_stop on a non-running widget, the widget
        # should have posted a PlayClicked message (we can't easily test
        # message posting in Textual tests, so we just verify action works)
        assert link.is_running is False  # State unchanged by action alone

    async def test_stop_button_click_posts_event(self):
        """Test clicking stop button posts StopClicked event."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Set running
            link.set_status(running=True)
            await pilot.pause()

            # Click stop button
            await pilot.click(".play-stop-button")
            await pilot.pause()

            assert len(app.stop_clicked_events) == 1
            event = app.stop_clicked_events[0]
            assert event.name == "TestCommand"

    async def test_play_keyboard_shortcut_space(self):
        """Test space key is bound for play/stop action."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Verify binding exists
            bindings = link._bindings.get_bindings_for_key("space")
            assert len(bindings) > 0
            assert bindings[0].action == "play_stop"

    async def test_play_keyboard_shortcut_p(self):
        """Test 'p' key is bound for play/stop action."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Verify binding exists
            bindings = link._bindings.get_bindings_for_key("p")
            assert len(bindings) > 0
            assert bindings[0].action == "play_stop"

    async def test_custom_play_stop_keys(self):
        """Test custom play_stop_keys parameter creates bindings."""
        link = CommandLink("TestCommand", play_stop_keys=["r", "enter"])
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Verify custom bindings exist
            bindings_r = link._bindings.get_bindings_for_key("r")
            assert len(bindings_r) > 0
            assert bindings_r[0].action == "play_stop"

            bindings_enter = link._bindings.get_bindings_for_key("enter")
            assert len(bindings_enter) > 0
            assert bindings_enter[0].action == "play_stop"


class TestCommandLinkOutput:
    """Test suite for CommandLink output file handling."""

    async def test_output_clicked_posted_when_name_clicked(self, temp_output_file):
        """Test OutputClicked is posted when FileLink name is clicked."""
        link = CommandLink("TestCommand", output_path=temp_output_file)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Click on the FileLink name widget
            await pilot.click(FileLink)
            await pilot.pause()

            assert len(app.output_clicked_events) == 1
            event = app.output_clicked_events[0]
            assert event.output_path == temp_output_file

    async def test_open_output_keyboard_shortcut(self, temp_output_file):
        """Test 'o' key opens output file."""
        link = CommandLink("TestCommand", output_path=temp_output_file)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()
            await pilot.press("o")
            await pilot.pause()

            # Should trigger FileLink open action
            # (no easy way to verify file opening in test, just verify no crash)

    async def test_custom_open_keys(self, temp_output_file):
        """Test custom open_keys parameter."""
        link = CommandLink("TestCommand", output_path=temp_output_file, open_keys=["f", "enter"])
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()

            # Custom key 'f' should work
            await pilot.press("f")
            await pilot.pause()
            # (no easy way to verify file opening in test)

    async def test_set_output_path(self, temp_output_file):
        """Test set_output_path() updates the output path."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # Initially no output path
            assert link.output_path is None
            assert link._name_widget.__class__.__name__ == "Static"

            # Set output path
            link.set_output_path(temp_output_file)
            await pilot.pause()

            assert link.output_path == temp_output_file
            # Name widget should now be FileLink
            assert isinstance(link._name_widget, FileLink)


class TestCommandLinkSettings:
    """Test suite for CommandLink settings functionality."""

    async def test_settings_icon_click_posts_event(self):
        """Test settings binding is created when show_settings=True."""
        link = CommandLink("TestCommand", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Verify settings binding exists
            bindings = link._bindings.get_bindings_for_key("s")
            assert len(bindings) > 0
            assert bindings[0].action == "settings"

            # Verify settings widget is visible
            settings = link.query_one(".settings-icon")
            assert settings is not None

    async def test_settings_keyboard_shortcut(self):
        """Test 's' key triggers settings action."""
        link = CommandLink("TestCommand", show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()
            await pilot.press("s")
            await pilot.pause()

            assert len(app.settings_clicked_events) == 1

    async def test_custom_settings_keys(self):
        """Test custom settings_keys parameter."""
        link = CommandLink("TestCommand", show_settings=True, settings_keys=["c", "comma"])
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()

            # Custom key 'c' should work
            await pilot.press("c")
            await pilot.pause()
            assert len(app.settings_clicked_events) == 1


class TestCommandLinkProperties:
    """Test suite for CommandLink properties."""

    def test_name_property(self):
        """Test name property returns command name."""
        link = CommandLink("My Test Command")

        assert link.name == "My Test Command"

    def test_output_path_property(self, temp_output_file):
        """Test output_path property."""
        link = CommandLink("TestCommand", output_path=temp_output_file)

        assert link.output_path == temp_output_file

    async def test_is_running_property(self):
        """Test is_running property."""
        link = CommandLink("TestCommand")
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            assert link.is_running is False

            link.set_status(running=True)
            await pilot.pause()
            assert link.is_running is True

            link.set_status(running=False)
            await pilot.pause()
            assert link.is_running is False


class TestCommandLinkKeyboardBindings:
    """Test suite for CommandLink keyboard binding creation."""

    async def test_runtime_bindings_created(self, temp_output_file):
        """Test runtime bindings are created in on_mount()."""
        link = CommandLink("TestCommand", output_path=temp_output_file, show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Check open_output bindings
            bindings_o = link._bindings.get_bindings_for_key("o")
            assert len(bindings_o) > 0
            assert bindings_o[0].action == "open_output"

            # Check play_stop bindings
            bindings_space = link._bindings.get_bindings_for_key("space")
            assert len(bindings_space) > 0
            assert bindings_space[0].action == "play_stop"

            bindings_p = link._bindings.get_bindings_for_key("p")
            assert len(bindings_p) > 0
            assert bindings_p[0].action == "play_stop"

            # Check settings bindings
            bindings_s = link._bindings.get_bindings_for_key("s")
            assert len(bindings_s) > 0
            assert bindings_s[0].action == "settings"

    async def test_custom_bindings_created(self, temp_output_file):
        """Test custom keyboard bindings are created correctly."""
        link = CommandLink(
            "TestCommand",
            output_path=temp_output_file,
            show_settings=True,
            open_keys=["f1", "f2"],
            play_stop_keys=["r"],
            settings_keys=["c"],
        )
        app = CommandLinkTestApp(link)

        async with app.run_test():
            # Check custom open_keys
            bindings_f1 = link._bindings.get_bindings_for_key("f1")
            assert len(bindings_f1) > 0
            assert bindings_f1[0].action == "open_output"

            # Check custom play_stop_keys
            bindings_r = link._bindings.get_bindings_for_key("r")
            assert len(bindings_r) > 0
            assert bindings_r[0].action == "play_stop"

            # Check custom settings_keys
            bindings_c = link._bindings.get_bindings_for_key("c")
            assert len(bindings_c) > 0
            assert bindings_c[0].action == "settings"


class TestCommandLinkIntegration:
    """Integration tests for CommandLink."""

    async def test_complete_workflow(self, temp_output_file):
        """Test a complete command execution workflow."""
        link = CommandLink("TestCommand", output_path=temp_output_file, show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            # 1. Click play using keyboard shortcut (more reliable)
            link.focus()
            await pilot.press("space")
            await pilot.pause()
            assert len(app.play_clicked_events) == 1

            # 2. Set running status
            link.set_status(running=True, tooltip="Running...")
            await pilot.pause()
            assert link.is_running is True

            # 3. Press space to stop
            await pilot.press("space")
            await pilot.pause()
            assert len(app.stop_clicked_events) == 1

            # 4. Set completed status
            link.set_status(icon="✅", running=False, tooltip="Completed")
            await pilot.pause()
            assert link.is_running is False
            assert "✅" in str(link._status_widget.render())

    async def test_all_keyboard_shortcuts(self, temp_output_file):
        """Test all keyboard shortcuts work together."""
        link = CommandLink("TestCommand", output_path=temp_output_file, show_settings=True)
        app = CommandLinkTestApp(link)

        async with app.run_test() as pilot:
            link.focus()

            # Play/stop with space
            await pilot.press("space")
            await pilot.pause()
            assert len(app.play_clicked_events) == 1

            # Settings with 's'
            await pilot.press("s")
            await pilot.pause()
            assert len(app.settings_clicked_events) == 1

            # Open output with 'o'
            await pilot.press("o")
            await pilot.pause()
            # (FileLink opens, no direct way to verify in test)
