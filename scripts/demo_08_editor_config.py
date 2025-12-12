"""Demo 8: Custom Editor Configuration - Flexible Editor Support

This demo shows how to use different editors and customize file opening behavior.

Demonstrates:
- All 5 built-in editors (VSCode, Vim, Nano, Eclipse, Copy Path)
- Custom command builders for other editors (Sublime, IntelliJ, Emacs)
- Environment variable detection ($EDITOR)
- Auto-detection with fallback chain
- Per-instance vs class-level configuration

Real-world use cases:
- Multi-editor teams where developers use different IDEs
- Server environments where VSCode isn't available
- Custom tools requiring specific editor integration
- User preference adaptation

Key patterns:
- FileLink.vscode_command, vim_command, nano_command, etc.
- Custom command_builder functions
- Editor auto-detection with fallback chains
- os.environ for environment variable access
- shutil.which() for command availability checking

Prerequisites:
- Understand demo_01 (FileLink basics)
- Basic understanding of command-line editors

Notes:
- All editors work with the sample_files/example.py file
- Without VSCode installed, the demo shows graceful fallback
- Custom editors demonstrate the pattern you can use for any editor
"""

import os
import shutil
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header, Static

from textual_filelink import FileLink


# Helper functions for editor auto-detection and custom builders

def detect_available_editor() -> str:
    """Auto-detect which editor is available on this system.

    Checks in order: $EDITOR environment variable, then VSCode, Vim, Nano.
    Returns the first one found, defaulting to 'copy' if nothing else available.
    """
    # First check environment variable
    if editor := os.environ.get('EDITOR'):
        return editor

    # Try common editors in preferred order
    for cmd in ['code', 'vim', 'nano']:
        if shutil.which(cmd):
            return cmd

    # Fallback - always works
    return 'copy'


def custom_sublime_command(path: Path, line: int | None, column: int | None) -> list[str]:
    """Custom command builder for Sublime Text.

    Sublime Text uses format: subl file.py:line:column

    Parameters
    ----------
    path : Path
        File to open
    line : int | None
        Line number (1-indexed)
    column : int | None
        Column number (1-indexed)

    Returns
    -------
    list[str]
        Command and arguments for subprocess execution
    """
    location = f"{path}:{line or 1}:{column or 1}"
    return ["subl", location]


def custom_intellij_command(path: Path, line: int | None, column: int | None) -> list[str]:
    """Custom command builder for IntelliJ IDEA and related IDEs.

    IntelliJ format: idea --line line --column column file.py

    Works with: IntelliJ IDEA, PyCharm, WebStorm, RubyMine, etc.
    """
    cmd = ["idea"]
    if line is not None:
        cmd.extend(["--line", str(line)])
    if column is not None:
        cmd.extend(["--column", str(column)])
    cmd.append(str(path))
    return cmd


def custom_emacs_command(path: Path, line: int | None, column: int | None) -> list[str]:
    """Custom command builder for Emacs.

    Emacs format: emacs +line:column file.py

    Note: Emacs uses +line:column syntax where both are optional
    """
    if line is not None and column is not None:
        location = f"+{line}:{column}"
        return ["emacs", location, str(path)]
    elif line is not None:
        return ["emacs", f"+{line}", str(path)]
    return ["emacs", str(path)]


class EditorConfigApp(App):
    """Demonstrate editor configuration flexibility."""

    TITLE = "Demo 8: Custom Editor Configuration - Flexible Editor Support"
    BINDINGS = [("q", "quit", "Quit")]

    CSS = """
    Screen {
        layout: vertical;
    }

    #title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $boost;
    }

    #content {
        width: 100%;
        height: 1fr;
        overflow: auto;
        padding: 1;
    }

    .section-title {
        width: 100%;
        text-style: bold;
        color: $primary;
        margin: 2 0 1 0;
    }

    .section-description {
        width: 100%;
        color: $text-muted;
        margin: 0 0 1 0;
        height: auto;
    }

    .file-link-hint {
        width: 100%;
        color: $text-muted;
        margin: 0 0 1 0;
        height: auto;
    }

    FileLink {
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI with editor configuration examples."""
        yield Header()

        yield Static("📝 Editor Configuration - Choose Your Tool", id="title")

        with ScrollableContainer(id="content"):
            # Section 1: Built-in Editors
            yield Static("Section 1: Built-in Editors", classes="section-title")
            yield Static(
                "FileLink includes 5 built-in editor support options. "
                "Click any file to open it with the configured editor.",
                classes="section-description",
            )

            sample_file = Path("sample_files/example.py")

            yield Static("VSCode (Default)", classes="section-title")
            yield Static(
                "Modern, feature-rich editor. Falls back to another editor if VSCode not installed.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.vscode_command,
                tooltip="Opens with: code file.py:line:column",
            )

            yield Static("Vim (Command Line)", classes="section-title")
            yield Static(
                "Lightweight, powerful terminal editor. Available on almost all systems.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.vim_command,
                tooltip="Opens with: vim +line file.py",
            )

            yield Static("Nano (Beginner-friendly)", classes="section-title")
            yield Static(
                "Simple terminal editor. Best for quick edits, included on most systems.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.nano_command,
                tooltip="Opens with: nano +line file.py",
            )

            yield Static("Eclipse IDE", classes="section-title")
            yield Static(
                "Full-featured Java IDE. Also supports other languages with plugins.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.eclipse_command,
                tooltip="Opens with: eclipse file.py",
            )

            yield Static("Copy Path to Clipboard", classes="section-title")
            yield Static(
                "No editor needed - just copies the file path. Useful for reference or piping.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.copy_path_command,
                tooltip="Copies path to clipboard instead of opening",
            )

            # Section 2: Custom Command Builders
            yield Static("Section 2: Custom Command Builders", classes="section-title")
            yield Static(
                "Define custom builders for any editor. "
                "Each builder is a function: (path, line, column) → [command, args...]",
                classes="section-description",
            )

            yield Static("Sublime Text (Custom)", classes="section-title")
            yield Static(
                "Pattern: subl file.py:line:column. Useful for teams using Sublime.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=custom_sublime_command,
                tooltip="Opens with: subl file.py:line:column",
            )

            yield Static("IntelliJ IDEA (Custom)", classes="section-title")
            yield Static(
                "Pattern: idea --line N --column N file.py. Works for PyCharm, RubyMine, etc.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=custom_intellij_command,
                tooltip="Opens with: idea --line N --column N file.py",
            )

            yield Static("Emacs (Custom)", classes="section-title")
            yield Static(
                "Pattern: emacs +line:column file.py. For Emacs power users.",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=custom_emacs_command,
                tooltip="Opens with: emacs +line:column file.py",
            )

            # Section 3: Environment Variable Detection
            yield Static("Section 3: Environment Variables", classes="section-title")
            yield Static(
                f"Current $EDITOR setting: {os.environ.get('EDITOR', 'not set')}",
                classes="file-link-hint",
            )
            yield Static(
                "Your app can read $EDITOR to respect user preferences:",
                classes="file-link-hint",
            )
            yield FileLink(
                sample_file,
                command_builder=FileLink.vim_command,
                tooltip="Using $EDITOR=vim from environment",
            )

            # Section 4: Auto-detection with Fallback
            yield Static("Section 4: Auto-Detection with Fallback Chain", classes="section-title")
            detected_editor = detect_available_editor()
            yield Static(
                f"Auto-detected available editor: {detected_editor}\n"
                f"Detection order: $EDITOR → code → vim → nano → copy",
                classes="file-link-hint",
            )

            # Map detected editor to command builder
            editor_map = {
                'code': FileLink.vscode_command,
                'vim': FileLink.vim_command,
                'nano': FileLink.nano_command,
                'copy': FileLink.copy_path_command,
            }
            builder = editor_map.get(detected_editor, FileLink.vim_command)
            yield FileLink(
                sample_file,
                command_builder=builder,
                tooltip=f"Using auto-detected editor: {detected_editor}",
            )

            # Section 5: Class-level vs Per-instance Configuration
            yield Static("Section 5: Configuration Levels", classes="section-title")
            yield Static(
                "Set default editor at class level (affects all FileLinks) "
                "or per-instance (specific FileLink only).",
                classes="section-description",
            )
            yield Static(
                "Class-level (global default): FileLink.default_command_builder = custom_sublime_command",
                classes="file-link-hint",
            )
            yield Static(
                "Per-instance (this link only): FileLink(..., command_builder=custom_vim_command)",
                classes="file-link-hint",
            )

            # Example of per-instance override
            yield FileLink(
                sample_file,
                command_builder=FileLink.nano_command,
                tooltip="Per-instance override: uses Nano regardless of class default",
            )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize after mounting."""
        sample_dir = Path("./sample_files")
        if not sample_dir.exists():
            self.notify(
                "Warning: ./sample_files not found. File paths will be relative.",
                severity="warning",
                timeout=5,
            )


if __name__ == "__main__":
    app = EditorConfigApp()
    app.run()
