"""Demonstrate command template usage for opening files in different editors.

This example shows all the ways to use command templates:
1. Built-in template constants
2. Class-level default templates
3. Per-instance templates
4. Explicit builder from template
5. Priority order demonstration
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Static

from textual_filelink import CommandLink, FileLink, FileLinkWithIcons, Icon, command_from_template


class CommandTemplateDemo(App):
    """Demo app showing command template functionality."""

    CSS = """
    Screen {
        align: center middle;
    }

    VerticalScroll {
        width: 100%;
        height: auto;
        max-height: 80%;
        border: solid $accent;
        background: $panel;
        padding: 1;
    }

    .section-header {
        text-style: bold;
        background: $boost;
        padding: 1;
        margin-bottom: 1;
    }

    .demo-item {
        margin-bottom: 1;
        padding-left: 2;
    }

    .note {
        color: $text-muted;
        text-style: italic;
        padding-left: 4;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the demo UI."""
        yield Header()

        # Create a sample file to use in examples
        sample_file = Path(__file__).parent / "demo_01_filelink.py"

        with VerticalScroll():
            yield Static("Command Template Examples", classes="section-header")

            # Section 1: Built-in template constants
            yield Static("1. Built-in Template Constants", classes="section-header")
            yield Static("Use FileLink.VSCODE_TEMPLATE, VIM_TEMPLATE, etc. as shortcuts:", classes="note")

            yield FileLink(
                sample_file,
                line=10,
                command_template=FileLink.VSCODE_TEMPLATE,
                id="vscode-template",
                classes="demo-item",
            )
            yield Static(f"  Template: {FileLink.VSCODE_TEMPLATE}", classes="note")

            yield FileLink(
                sample_file, line=42, command_template=FileLink.VIM_TEMPLATE, id="vim-template", classes="demo-item"
            )
            yield Static(f"  Template: {FileLink.VIM_TEMPLATE}", classes="note")

            yield FileLink(
                sample_file,
                line=100,
                command_template=FileLink.SUBLIME_TEMPLATE,
                id="sublime-template",
                classes="demo-item",
            )
            yield Static(f"  Template: {FileLink.SUBLIME_TEMPLATE}", classes="note")

            # Section 2: Custom templates
            yield Static("2. Custom Templates", classes="section-header")
            yield Static("Create your own templates with any variable combination:", classes="note")

            # Custom format example
            yield FileLink(
                sample_file,
                line=20,
                column=5,
                command_template='myeditor "{{ path }}" --line {{ line }} --column {{ column }}',
                id="custom-template",
                classes="demo-item",
            )
            yield Static('  Template: myeditor "{{ path }}" --line {{ line }} --column {{ column }}', classes="note")

            # Filename only
            yield FileLink(
                sample_file, command_template="editor {{ path_name }}", id="filename-only", classes="demo-item"
            )
            yield Static("  Template: editor {{ path_name }}", classes="note")

            # Section 3: Using command_from_template explicitly
            yield Static("3. Explicit Builder from Template", classes="section-header")
            yield Static("Convert templates to builders with command_from_template():", classes="note")

            # Create builder explicitly
            emacs_builder = command_from_template("emacs {{ line_plus }} {{ path }}")
            yield FileLink(sample_file, line=50, command_builder=emacs_builder, id="emacs-builder", classes="demo-item")
            yield Static("  Builder: command_from_template('emacs {{ line_plus }} {{ path }}')", classes="note")

            # Section 4: With FileLinkWithIcons
            yield Static("4. Templates with FileLinkWithIcons", classes="section-header")
            yield Static("Templates work with all FileLink-based widgets:", classes="note")

            yield FileLinkWithIcons(
                sample_file,
                line=30,
                command_template=FileLink.VIM_TEMPLATE,
                icons_before=[Icon("status", "✓", "Status")],
                id="filelink-with-icons",
                classes="demo-item",
            )
            yield Static("  Using VIM_TEMPLATE with icons", classes="note")

            # Section 5: With CommandLink
            yield Static("5. Templates with CommandLink", classes="section-header")
            yield Static("CommandLink also supports command templates for output files:", classes="note")

            output_file = Path(__file__).parent / "demo_01_filelink.py"
            yield CommandLink(
                "Build Output",
                output_path=output_file,
                command_template=FileLink.SUBLIME_TEMPLATE,
                id="command-link",
                classes="demo-item",
            )
            yield Static("  Output file opens with SUBLIME_TEMPLATE", classes="note")

            # Section 6: Template variables reference
            yield Static("6. Available Template Variables", classes="section-header")
            yield Static("All available template variables:", classes="note")
            yield Static("  {{ path }}           - Full absolute path", classes="note")
            yield Static("  {{ path_relative }}  - Path relative to cwd", classes="note")
            yield Static("  {{ path_name }}      - Just the filename", classes="note")
            yield Static("  {{ line }}           - Line number", classes="note")
            yield Static("  {{ column }}         - Column number", classes="note")
            yield Static("  {{ line_colon }}     - :line format (e.g., :42)", classes="note")
            yield Static("  {{ column_colon }}   - :column format (e.g., :5)", classes="note")
            yield Static("  {{ line_plus }}      - +line format (e.g., +42)", classes="note")
            yield Static("  {{ column_plus }}    - +column format (e.g., +5)", classes="note")

            # Section 7: Priority order
            yield Static("7. Priority Order", classes="section-header")
            yield Static("When multiple command options are set, priority is:", classes="note")
            yield Static("  1. Instance command_builder (highest)", classes="note")
            yield Static("  2. Instance command_template", classes="note")
            yield Static("  3. Class default_command_builder", classes="note")
            yield Static("  4. Class default_command_template", classes="note")
            yield Static("  5. Built-in VSCode command (fallback)", classes="note")

        yield Footer()

    def on_mount(self) -> None:
        """Show notification on startup."""
        self.notify(
            "Click any file link to open (will use template). Press 'q' to quit.",
            title="Command Template Demo",
            timeout=5,
        )


if __name__ == "__main__":
    app = CommandTemplateDemo()
    app.run()
