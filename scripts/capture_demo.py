"""Capture screenshot of demo_commandlink.py for development feedback."""

import asyncio
from pathlib import Path
import sys

# Add the scripts directory to the path so we can import demo_commandlink
sys.path.insert(0, str(Path(__file__).parent))

from demo_commandlink import CommandOrchestratorApp


async def capture():
    """Run the app and capture a screenshot."""
    app = CommandOrchestratorApp()
    
    async with app.run_test(size=(80, 40)) as pilot:  # Set explicit terminal size
        # Wait for app to fully render
        await pilot.pause(2)
        
        # Make sure we're scrolled to the top
        await pilot.press("home")
        await pilot.pause(0.5)
        
        # Save screenshot as SVG (preserves colors and styling)
        pilot.app.save_screenshot("demo-snapshot.svg")
        print("✓ Screenshot saved to demo-snapshot.svg")
        
        # Also save as text for easier parsing
        pilot.app.save_screenshot("demo-snapshot.txt")
        print("✓ Text snapshot saved to demo-snapshot.txt")


if __name__ == "__main__":
    asyncio.run(capture())