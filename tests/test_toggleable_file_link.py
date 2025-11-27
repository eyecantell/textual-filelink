# tests/test_toggleable_file_link.py
import pytest
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static

from textual_filelink import FileLink, ToggleableFileLink


class ToggleableFileLinkTestApp(App):
    """Test app for ToggleableFileLink."""
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.toggled_events = []
        self.removed_events = []
        self.clicked_events = []
    
    def compose(self) -> ComposeResult:
        yield self.widget
    
    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.toggled_events.append(event)
    
    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.removed_events.append(event)
    
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
        assert link.status_icon is None
    
    async def test_initialization_with_toggle(self, temp_file):
        """Test ToggleableFileLink initializes with toggle state."""
        link = ToggleableFileLink(temp_file, initial_toggle=True)
        
        assert link.is_toggled is True
    
    async def test_initialization_with_status_icon(self, temp_file):
        """Test ToggleableFileLink initializes with status icon."""
        link = ToggleableFileLink(temp_file, status_icon="✓")
        
        assert link.status_icon == "✓"
    
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
    
    async def test_toggle_visual_update(self, temp_file):
        """Test toggle visual updates correctly."""
        link = ToggleableFileLink(temp_file, initial_toggle=False, show_toggle=True)
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            toggle_widget = link.query_one("#toggle", Static)
            assert toggle_widget.renderable == "☐"
            
            await pilot.click("#toggle")
            await pilot.pause()
            
            assert toggle_widget.renderable == "✓"
    
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
        link = ToggleableFileLink(
            temp_file, 
            show_toggle=True, 
            show_remove=False
        )
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            # Should have toggle
            assert link.query_one("#toggle", Static)
            
            # Should not have remove
            with pytest.raises(Exception):
                link.query_one("#remove", Static)
    
    async def test_remove_only_layout(self, temp_file):
        """Test layout with remove only (no toggle)."""
        link = ToggleableFileLink(
            temp_file,
            show_toggle=False,
            show_remove=True
        )
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            # Should not have toggle
            with pytest.raises(Exception):
                link.query_one("#toggle", Static)
            
            # Should have remove
            assert link.query_one("#remove", Static)
    
    async def test_no_controls_layout(self, temp_file):
        """Test layout with no controls."""
        link = ToggleableFileLink(
            temp_file,
            show_toggle=False,
            show_remove=False
        )
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            # Should not have toggle or remove
            with pytest.raises(Exception):
                link.query_one("#toggle", Static)
            with pytest.raises(Exception):
                link.query_one("#remove", Static)
    
    async def test_status_icon_displayed(self, temp_file):
        """Test status icon is displayed when provided."""
        link = ToggleableFileLink(temp_file, status_icon="⚠")
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            status_widget = link.query_one("#status-icon", Static)
            assert status_widget.renderable == "⚠"
    
    async def test_set_status_icon(self, temp_file):
        """Test updating status icon after creation."""
        link = ToggleableFileLink(temp_file, status_icon="✓")
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            assert link.status_icon == "✓"
            
            link.set_status_icon("⚠")
            await pilot.pause()
            
            assert link.status_icon == "⚠"
            status_widget = link.query_one("#status-icon", Static)
            assert status_widget.renderable == "⚠"
    
    async def test_set_status_icon_to_none(self, temp_file):
        """Test hiding status icon by setting to None."""
        link = ToggleableFileLink(temp_file, status_icon="✓")
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            link.set_status_icon(None)
            await pilot.pause()
            
            assert link.status_icon is None
            status_widget = link.query_one("#status-icon", Static)
            assert status_widget.display is False
    
    async def test_disable_on_untoggle(self, temp_file):
        """Test disable_on_untoggle adds disabled class."""
        link = ToggleableFileLink(
            temp_file,
            initial_toggle=False,
            disable_on_untoggle=True,
            show_toggle=True
        )
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
            await pilot.click(FileLink)
            await pilot.pause()
            
            assert len(app.clicked_events) == 1
            event = app.clicked_events[0]
            assert event.path == temp_file
            assert event.line == 10
            assert event.column == 5
    
    async def test_file_link_click_blocked_when_disabled(self, temp_file):
        """Test FileLink click is blocked when disable_on_untoggle is active."""
        link = ToggleableFileLink(
            temp_file,
            initial_toggle=False,
            disable_on_untoggle=True,
            show_toggle=True
        )
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
        
        async with app.run_test() as pilot:
            file_link = link.query_one(FileLink)
            assert file_link._command_builder == custom_builder
    
    async def test_line_and_column_passed_to_filelink(self, temp_file):
        """Test line and column are passed to internal FileLink."""
        link = ToggleableFileLink(temp_file, line=42, column=7)
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
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
    
    async def test_status_icon_property(self, temp_file):
        """Test status_icon property reflects current icon."""
        link = ToggleableFileLink(temp_file, status_icon="🔥")
        
        assert link.status_icon == "🔥"
    
    async def test_multiple_status_icon_updates(self, temp_file):
        """Test multiple status icon updates work correctly."""
        link = ToggleableFileLink(temp_file)
        app = ToggleableFileLinkTestApp(link)
        
        async with app.run_test() as pilot:
            icons = ["⏳", "✓", "⚠", "✗", None, "🔥"]
            
            for icon in icons:
                link.set_status_icon(icon)
                await pilot.pause()
                assert link.status_icon == icon