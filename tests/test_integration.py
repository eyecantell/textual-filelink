# Fixed test_integration.py
"""Integration tests for FileLink and ToggleableFileLink working together."""

import pytest
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Vertical

from textual_filelink import FileLink, ToggleableFileLink


class IntegrationTestApp(App):
    """Test app with multiple file links."""
    
    def __init__(self, file_links):
        super().__init__()
        self.file_links = file_links
        self.events = []
    
    def compose(self) -> ComposeResult:
        with Vertical():
            for link in self.file_links:
                yield link
    
    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.events.append(("toggled", event))
    
    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.events.append(("removed", event))
    
    def on_file_link_clicked(self, event: FileLink.Clicked):
        self.events.append(("clicked", event))


@pytest.mark.integration
class TestIntegration:
    """Integration tests for file link widgets."""
    
    async def test_multiple_filelinks(self, sample_files):
        """Test multiple FileLink widgets in a single app."""
        links = [FileLink(f) for f in sample_files]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            # All links should be present
            assert len(list(app.query(FileLink))) == len(sample_files)
    
    async def test_multiple_toggleable_filelinks(self, sample_files):
        """Test multiple ToggleableFileLink widgets."""
        links = [
            ToggleableFileLink(f, show_toggle=True, show_remove=True)
            for f in sample_files
        ]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            # All links should be present
            assert len(list(app.query(ToggleableFileLink))) == len(sample_files)
            
            # Toggle first link
            first_link = links[0]
            await pilot.click(first_link.query_one("#toggle"))
            await pilot.pause()
            
            assert first_link.is_toggled is True
            assert len([e for e in app.events if e[0] == "toggled"]) == 1
    
    async def test_mixed_filelink_types(self, sample_files):
        """Test mixing FileLink and ToggleableFileLink."""
        links = [
            FileLink(sample_files[0]),
            ToggleableFileLink(sample_files[1]),
            FileLink(sample_files[2]),
        ]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            assert len(list(app.query(FileLink))) == 3  # 2 FileLink + 1 inside ToggleableFileLink
            assert len(list(app.query(ToggleableFileLink))) == 1
    
    async def test_toggle_multiple_links(self, sample_files):
        """Test toggling multiple links independently."""
        links = [
            ToggleableFileLink(f, show_toggle=True)
            for f in sample_files[:3]
        ]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            # Toggle all links
            toggleables = list(app.query(ToggleableFileLink))
            for link in toggleables:
                await pilot.click(link.query_one("#toggle"))
                await pilot.pause()
            
            # All should be toggled
            assert all(link.is_toggled for link in links)
            assert len([e for e in app.events if e[0] == "toggled"]) == 3
    
    async def test_status_icons_on_multiple_links(self, sample_files):
        """Test different status icons on multiple links."""
        icons = ["✓", "⚠", "✗", "⏳", "🔥"]
        links = [
            ToggleableFileLink(f, status_icon=icons[i % len(icons)])
            for i, f in enumerate(sample_files)
        ]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            # Each link should have its assigned icon
            for i, link in enumerate(links):
                assert link.status_icon == icons[i % len(icons)]
    
    async def test_remove_multiple_links(self, sample_files):
        """Test removing multiple links."""
        links = [
            ToggleableFileLink(f, show_remove=True)
            for f in sample_files[:3]
        ]
        app = IntegrationTestApp(links)
        
        async with app.run_test() as pilot:
            # Remove all links
            toggleables = list(app.query(ToggleableFileLink))
            for link in toggleables:
                await pilot.click(link.query_one("#remove"))
                await pilot.pause()
            
            # Should have 3 remove events
            assert len([e for e in app.events if e[0] == "removed"]) == 3
    
    async def test_long_filename_rendering(self, long_filename, get_rendered_text):
        """Test rendering of very long filenames."""
        link = FileLink(long_filename)
        app = IntegrationTestApp([link])
        
        async with app.run_test() as pilot:
            # Should render without error
            assert get_rendered_text(link) == long_filename.name
    
    async def test_special_chars_filename(self, special_char_filename, get_rendered_text):
        """Test filenames with special characters."""
        link = ToggleableFileLink(
            special_char_filename,
            show_toggle=True,
            show_remove=True
        )
        app = IntegrationTestApp([link])
        
        async with app.run_test() as pilot:
            # Should handle special characters
            file_link = link.query_one(FileLink)
            assert get_rendered_text(file_link) == special_char_filename.name
            
            # Should be clickable
            await pilot.click(link.query_one("#toggle"))
            await pilot.pause()
            assert link.is_toggled is True
    
    async def test_unicode_filename(self, unicode_filename, get_rendered_text):
        """Test filenames with unicode characters."""
        link = ToggleableFileLink(unicode_filename, status_icon="🌟")
        app = IntegrationTestApp([link])
        
        async with app.run_test() as pilot:
            # Should handle unicode in filename and icon
            file_link = link.query_one(FileLink)
            assert get_rendered_text(file_link) == unicode_filename.name
            assert link.status_icon == "🌟"
    
    async def test_disable_on_untoggle_interaction(self, sample_files):
        """Test disable_on_untoggle affects click behavior."""
        link = ToggleableFileLink(
            sample_files[0],
            initial_toggle=False,
            disable_on_untoggle=True,
            show_toggle=True
        )
        app = IntegrationTestApp([link])
        
        async with app.run_test() as pilot:
            # Try clicking disabled link
            file_link = link.query_one(FileLink)
            await pilot.click(file_link)
            await pilot.pause()
            
            # Click should be blocked
            assert len([e for e in app.events if e[0] == "clicked"]) == 0
            
            # Enable by toggling
            await pilot.click(link.query_one("#toggle"))
            await pilot.pause()
            
            # Now click should work
            await pilot.click(file_link)
            await pilot.pause()
            
            assert len([e for e in app.events if e[0] == "clicked"]) == 1
    
    async def test_all_features_combined(self, sample_files):
        """Test all features working together."""
        link = ToggleableFileLink(
            sample_files[0],
            initial_toggle=True,
            show_toggle=True,
            show_remove=True,
            status_icon="✓",
            line=42,
            column=10,
            disable_on_untoggle=False
        )
        app = IntegrationTestApp([link])
        
        async with app.run_test() as pilot:
            # Should start toggled
            assert link.is_toggled is True
            assert link.status_icon == "✓"
            
            # Change status icon
            link.set_status_icon("⚠")
            await pilot.pause()
            assert link.status_icon == "⚠"
            
            # Click the file
            await pilot.click(FileLink)
            await pilot.pause()
            
            clicked_events = [e for e in app.events if e[0] == "clicked"]
            assert len(clicked_events) == 1
            assert clicked_events[0][1].line == 42
            assert clicked_events[0][1].column == 10
            
            # Toggle off
            await pilot.click(link.query_one("#toggle"))
            await pilot.pause()
            assert link.is_toggled is False
            
            # Remove
            await pilot.click(link.query_one("#remove"))
            await pilot.pause()
            
            removed_events = [e for e in app.events if e[0] == "removed"]
            assert len(removed_events) == 1