# Updated test_integration.py with multi-icon support
"""Integration tests for FileLink and ToggleableFileLink working together."""

import pytest
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
            yield from self.file_links

    def on_toggleable_file_link_toggled(self, event: ToggleableFileLink.Toggled):
        self.events.append(("toggled", event))

    def on_toggleable_file_link_removed(self, event: ToggleableFileLink.Removed):
        self.events.append(("removed", event))

    def on_toggleable_file_link_icon_clicked(self, event: ToggleableFileLink.IconClicked):
        self.events.append(("icon_clicked", event))

    def on_file_link_clicked(self, event):
        self.events.append(("clicked", event))


@pytest.mark.integration
class TestIntegration:
    """Integration tests for file link widgets."""

    async def test_multiple_filelinks(self, sample_files):
        """Test multiple FileLink widgets in a single app."""
        links = [FileLink(f) for f in sample_files]
        app = IntegrationTestApp(links)

        async with app.run_test():
            # All links should be present
            assert len(list(app.query(FileLink))) == len(sample_files)

    async def test_multiple_toggleable_filelinks(self, sample_files):
        """Test multiple ToggleableFileLink widgets."""
        links = [ToggleableFileLink(f, show_toggle=True, show_remove=True) for f in sample_files]
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

        async with app.run_test():
            assert len(list(app.query(FileLink))) == 3  # 2 FileLink + 1 inside ToggleableFileLink
            assert len(list(app.query(ToggleableFileLink))) == 1

    async def test_toggle_multiple_links(self, sample_files):
        """Test toggling multiple links independently."""
        links = [ToggleableFileLink(f, show_toggle=True) for f in sample_files[:3]]
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

    async def test_multiple_icons_on_multiple_links(self, sample_files):
        """Test different icon configurations on multiple links."""
        links = [
            ToggleableFileLink(
                sample_files[0],
                icons=[
                    {"name": "status", "icon": "✓"},
                    {"name": "lock", "icon": "🔒"},
                ],
            ),
            ToggleableFileLink(
                sample_files[1],
                icons=[
                    {"name": "warning", "icon": "⚠"},
                    {"name": "progress", "icon": "⏳"},
                ],
            ),
            ToggleableFileLink(
                sample_files[2],
                icons=[
                    {"name": "error", "icon": "✗"},
                ],
            ),
        ]
        app = IntegrationTestApp(links)

        async with app.run_test():
            # Each link should have its icons
            assert len(links[0].icons) == 2
            assert len(links[1].icons) == 2
            assert len(links[2].icons) == 1

    async def test_remove_multiple_links(self, sample_files):
        """Test removing multiple links."""
        links = [ToggleableFileLink(f, show_remove=True) for f in sample_files[:3]]
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

        async with app.run_test():
            # Should render without error
            assert get_rendered_text(link) == long_filename.name

    async def test_special_chars_filename(self, special_char_filename, get_rendered_text):
        """Test filenames with special characters."""
        link = ToggleableFileLink(special_char_filename, show_toggle=True, show_remove=True)
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
        link = ToggleableFileLink(unicode_filename, icons=[{"name": "star", "icon": "🌟"}])
        app = IntegrationTestApp([link])

        async with app.run_test():
            # Should handle unicode in filename and icon
            file_link = link.query_one(FileLink)
            assert get_rendered_text(file_link) == unicode_filename.name
            assert link.icons[0]["icon"] == "🌟"

    async def test_disable_on_untoggle_interaction(self, sample_files):
        """Test disable_on_untoggle affects click behavior."""
        link = ToggleableFileLink(sample_files[0], initial_toggle=False, disable_on_untoggle=True, show_toggle=True)
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
            icons=[
                {"name": "status", "icon": "✓", "clickable": True, "tooltip": "Done"},
                {"name": "lock", "icon": "🔒", "position": "after"},
            ],
            line=42,
            column=10,
            disable_on_untoggle=False,
        )
        app = IntegrationTestApp([link])

        async with app.run_test() as pilot:
            # Should start toggled
            assert link.is_toggled is True
            assert len(link.icons) == 2

            # Click the status icon
            await pilot.click("#icon-status")
            await pilot.pause()

            icon_clicked_events = [e for e in app.events if e[0] == "icon_clicked"]
            assert len(icon_clicked_events) == 1
            assert icon_clicked_events[0][1].icon_name == "status"

            # Change icon dynamically
            link.update_icon("status", icon="⚠", tooltip="Warning")
            await pilot.pause()
            assert link.get_icon("status")["icon"] == "⚠"

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

    async def test_dynamic_icon_updates_across_links(self, sample_files):
        """Test dynamically updating icons on multiple links."""
        links = [
            ToggleableFileLink(
                f,
                icons=[
                    {"name": "status", "icon": "⏳", "visible": True},
                ],
            )
            for f in sample_files[:3]
        ]
        app = IntegrationTestApp(links)

        async with app.run_test() as pilot:
            # Update all icons to show completion
            for link in links:
                link.update_icon("status", icon="✓")
                await pilot.pause()

            # All should show checkmark
            for link in links:
                assert link.get_icon("status")["icon"] == "✓"

    async def test_icon_visibility_toggle_across_links(self, sample_files):
        """Test toggling icon visibility across multiple links."""
        links = [
            ToggleableFileLink(
                f,
                icons=[
                    {"name": "status", "icon": "✓", "visible": True},
                ],
            )
            for f in sample_files[:3]
        ]
        app = IntegrationTestApp(links)

        async with app.run_test() as pilot:
            # Hide all icons
            for link in links:
                link.set_icon_visible("status", False)
                await pilot.pause()

            # All should be hidden
            for link in links:
                assert link.get_icon("status")["visible"] is False

    async def test_mixed_icon_positions(self, sample_files):
        """Test links with icons in different positions."""
        links = [
            ToggleableFileLink(
                sample_files[0],
                icons=[
                    {"name": "before1", "icon": "🔥", "position": "before"},
                    {"name": "before2", "icon": "⭐", "position": "before"},
                ],
            ),
            ToggleableFileLink(
                sample_files[1],
                icons=[
                    {"name": "after1", "icon": "✓", "position": "after"},
                    {"name": "after2", "icon": "🔒", "position": "after"},
                ],
            ),
            ToggleableFileLink(
                sample_files[2],
                icons=[
                    {"name": "before", "icon": "⚠", "position": "before"},
                    {"name": "after", "icon": "✓", "position": "after"},
                ],
            ),
        ]
        app = IntegrationTestApp(links)

        async with app.run_test():
            # All icons should be present
            assert links[0].query_one("#icon-before1")
            assert links[0].query_one("#icon-before2")
            assert links[1].query_one("#icon-after1")
            assert links[1].query_one("#icon-after2")
            assert links[2].query_one("#icon-before")
            assert links[2].query_one("#icon-after")

    async def test_clickable_icons_across_links(self, sample_files):
        """Test clicking icons on multiple links."""
        links = [
            ToggleableFileLink(
                f,
                icons=[
                    {"name": "action", "icon": "🔔", "clickable": True},
                ],
            )
            for f in sample_files[:3]
        ]
        app = IntegrationTestApp(links)

        async with app.run_test() as pilot:
            # Click all icons
            for link in links:
                await pilot.click(link.query_one("#icon-action"))
                await pilot.pause()

            # Should have 3 icon click events
            icon_clicked_events = [e for e in app.events if e[0] == "icon_clicked"]
            assert len(icon_clicked_events) == 3

            # All should be for the "action" icon
            for event_tuple in icon_clicked_events:
                assert event_tuple[1].icon_name == "action"

    async def test_backwards_compat_status_icon_in_integration(self, sample_files):
        """Test backwards compatibility with old status_icon in integration."""
        with pytest.warns(DeprecationWarning):
            links = [ToggleableFileLink(f, status_icon="✓", status_icon_clickable=True) for f in sample_files[:2]]

        app = IntegrationTestApp(links)

        async with app.run_test():
            # Old API should still work
            for link in links:
                assert len(link.icons) == 1
                assert link.icons[0]["name"] == "status"
                assert link.icons[0]["clickable"] is True
