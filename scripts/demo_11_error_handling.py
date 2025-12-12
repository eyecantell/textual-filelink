"""Demo 11: Error Handling Patterns - Robust File Operation Validation

This demo teaches defensive programming for file operations.

Demonstrates:
- File validation helpers (reusable functions)
- Common error scenarios with user-friendly messages
- Permission checking and symlink handling
- Large file warnings
- Editor availability validation
- Custom exception design

Real-world use cases:
- Validating user-selected files before processing
- Safe file opening with graceful fallbacks
- Building reliable file management tools
- User-friendly error messages instead of crashes
- Protecting against race conditions and permissions issues

Key patterns:
- Validation function design: (bool, str) tuple returns
- Symlink resolution with strict mode
- os.access() for permission checking
- shutil.which() for editor availability
- Custom exceptions with context

Prerequisites:
- Understand demo_01 (FileLink basics)
- Basic understanding of file systems and permissions

Notes:
- All validators are reusable across your application
- Common errors are demonstrated with solutions
- Error messages include suggested fixes
- Symlink handling prevents common security issues
"""

import os
import shutil
from enum import Enum
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Footer, Header, Static

from textual_filelink import FileLink


# Custom exception with context
class FileLinkValidationError(Exception):
    """Raised when file validation fails during link operations."""

    def __init__(self, path: Path, reason: str, suggestion: str = ""):
        self.path = path
        self.reason = reason
        self.suggestion = suggestion
        message = f"Cannot open {path.name}: {reason}"
        if suggestion:
            message += f" → {suggestion}"
        super().__init__(message)


# Error type enumeration
class FileError(Enum):
    """Types of file errors that can occur."""

    NOT_FOUND = "not_found"
    NO_PERMISSION = "no_permission"
    IS_DIRECTORY = "is_directory"
    BROKEN_SYMLINK = "broken_symlink"
    TOO_LARGE = "too_large"
    EDITOR_MISSING = "editor_missing"


# Validation helper functions (reusable)


def validate_file_exists(path: Path) -> tuple[bool, str]:
    """Validate that file exists.

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    if not path.exists():
        return False, f"❌ File not found: {path.name}\n→ Check path spelling or location"
    if not path.is_file():
        return False, f"❌ Path is a directory: {path.name}\n→ Select a file, not a directory"
    return True, "✅ OK"


def validate_permissions(path: Path) -> tuple[bool, str]:
    """Validate that file is readable.

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    if not os.access(path, os.R_OK):
        return False, f"🔒 No read permission: {path.name}\n→ Run: chmod +r {path}"
    return True, "✅ OK"


def validate_file_size(path: Path, max_mb: int = 100) -> tuple[bool, str]:
    """Validate that file is under size limit.

    Large files may be slow to open or cause memory issues.

    Parameters
    ----------
    path : Path
        File to check
    max_mb : int
        Maximum size in megabytes (default: 100)

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    try:
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_mb:
            return (
                False,
                f"⚠️ Large file: {size_mb:.1f} MB (max {max_mb} MB)\n→ May be slow to open. Proceed?",
            )
        return True, "✅ OK"
    except OSError as e:
        return False, f"⚠️ Cannot check file size: {e}"


def validate_symlink(path: Path) -> tuple[bool, str]:
    """Validate symlink targets exist and aren't circular.

    Symlinks can point to missing files or create circular references.
    This validates the symlink is safe to follow.

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    if not path.is_symlink():
        return True, "✅ OK"  # Not a symlink, no issue

    try:
        # strict=True raises FileNotFoundError if target missing
        target = path.resolve(strict=True)
        return True, f"✅ OK (symlink → {target.name})"
    except RuntimeError:
        return False, f"🔗 Circular symlink: {path.name}\n→ Remove or update the symlink"
    except (FileNotFoundError, OSError):
        return False, f"🔗 Broken symlink: {path.name}\n→ Target file is missing"


def validate_editor_available(editor: str) -> tuple[bool, str]:
    """Validate that editor command exists on system.

    Uses shutil.which() to check if command is in PATH.

    Parameters
    ----------
    editor : str
        Editor command name (e.g., 'vim', 'code', 'nano')

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    if not shutil.which(editor):
        return False, f"⚠️ Editor not found: {editor}\n→ Install {editor} or use: vim, nano"
    return True, f"✅ {editor} available"


def validate_all(path: Path) -> tuple[bool, list[str]]:
    """Run all validations and collect all errors.

    This comprehensive validation checks everything and returns
    all issues found, not just the first one.

    Parameters
    ----------
    path : Path
        File to validate

    Returns
    -------
    tuple[bool, list[str]]
        (all_pass, list_of_errors)
    """
    errors = []

    # Check existence and type
    success, msg = validate_file_exists(path)
    if not success:
        errors.append(msg)
        return False, errors  # Can't continue if file doesn't exist

    # Check permissions
    success, msg = validate_permissions(path)
    if not success:
        errors.append(msg)

    # Check size (warning, not blocker)
    success, msg = validate_file_size(path)
    if not success:
        errors.append(msg)

    # Check symlinks
    success, msg = validate_symlink(path)
    if not success:
        errors.append(msg)

    return len(errors) == 0, errors


def get_error_type(path: Path) -> FileError | None:
    """Determine the type of error for a path.

    Useful for categorizing errors and providing targeted help.

    Returns
    -------
    FileError | None
        Error type if validation fails, None if all checks pass
    """
    if not path.exists():
        return FileError.NOT_FOUND
    if path.is_dir():
        return FileError.IS_DIRECTORY
    if path.is_symlink():
        try:
            path.resolve(strict=True)
        except (FileNotFoundError, RuntimeError):
            return FileError.BROKEN_SYMLINK
    if not os.access(path, os.R_OK):
        return FileError.NO_PERMISSION
    if (path.stat().st_size / (1024 * 1024)) > 100:
        return FileError.TOO_LARGE
    return None


class ErrorHandlingApp(App):
    """Demonstrate error handling and validation patterns."""

    TITLE = "Demo 11: Error Handling Patterns - Defensive Programming"
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

    .error-message {
        width: 100%;
        color: $error;
        margin: 0 0 1 0;
        height: auto;
    }

    FileLink {
        margin: 0 0 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the UI with error handling examples."""
        yield Header()

        yield Static("⚠️ Error Handling Patterns - Validation & Graceful Failures", id="title")

        with ScrollableContainer(id="content"):
            # Intro
            yield Static(
                "Error Handling Philosophy",
                classes="section-title",
            )
            yield Static(
                "Always validate before operating. Provide clear, actionable error messages. "
                "Never crash - always have a graceful degradation or fallback.",
                classes="section-description",
            )

            sample_dir = Path("./sample_files")
            if not sample_dir.exists():
                sample_dir = Path(".")

            # Section 1: File Not Found
            yield Static("Scenario 1: File Not Found", classes="section-title")
            yield Static(
                "Validator: validate_file_exists(). "
                "User selected a file that doesn't exist or was moved.",
                classes="section-description",
            )
            yield Static(
                "❌ File not found: missing_file.py\n→ Check path spelling or location",
                classes="error-message",
            )
            # Show a valid file as fallback
            valid_file = sample_dir / "example.py" if (sample_dir / "example.py").exists() else None
            if valid_file:
                yield FileLink(
                    valid_file,
                    tooltip="Fallback: this file exists and is valid",
                )

            # Section 2: Permission Denied
            yield Static("Scenario 2: Permission Denied", classes="section-title")
            yield Static(
                "Validator: validate_permissions(). "
                "File exists but user doesn't have read access (common in team environments).",
                classes="section-description",
            )
            yield Static(
                "🔒 No read permission: readonly_file.py\n→ Run: chmod +r readonly_file.py",
                classes="error-message",
            )
            yield Static(
                "Or contact your team lead if this is a protected file.",
                classes="section-description",
            )

            # Section 3: Wrong Type (Directory)
            yield Static("Scenario 3: Directory Instead of File", classes="section-title")
            yield Static(
                "Validator: validate_file_exists() with is_file() check. "
                "User accidentally selected a directory.",
                classes="section-description",
            )
            yield Static(
                "❌ Path is a directory: my_folder\n→ Select a file, not a directory",
                classes="error-message",
            )

            # Section 4: Broken Symlink
            yield Static("Scenario 4: Broken Symlink", classes="section-title")
            yield Static(
                "Validator: validate_symlink(). "
                "File is a symlink pointing to a missing target.",
                classes="section-description",
            )
            yield Static(
                "🔗 Broken symlink: old_link → missing.py\n→ Target file is missing or moved",
                classes="error-message",
            )
            yield Static(
                "Solution: Update symlink with 'ln -s new_target old_link' or delete it.",
                classes="section-description",
            )

            # Section 5: Valid Symlink
            yield Static("Scenario 5: Valid Symlink (Works Fine)", classes="section-title")
            yield Static(
                "Symlinks to existing files work perfectly. "
                "validate_symlink() ensures the target exists before opening.",
                classes="section-description",
            )
            if valid_file:
                yield FileLink(
                    valid_file,
                    tooltip="This file is readable and valid",
                )

            # Section 6: Large File Warning
            yield Static("Scenario 6: Large File Warning", classes="section-title")
            yield Static(
                "Validator: validate_file_size(). "
                "File exists and is readable, but it's large and may be slow to open.",
                classes="section-description",
            )
            yield Static(
                "⚠️ Large file: database_dump.sql (850 MB, max 100 MB)\n→ May be slow to open. Proceed?",
                classes="error-message",
            )
            yield Static(
                "Pattern: Warn user but still allow opening (their choice).",
                classes="section-description",
            )

            # Section 7: Editor Missing
            yield Static("Scenario 7: Editor Not Available", classes="section-title")
            yield Static(
                "Validator: validate_editor_available(). "
                "Requested editor is not installed on this system.",
                classes="section-description",
            )
            yield Static(
                "⚠️ Editor not found: sublime_text\n→ Install sublime_text or use: vim, nano, code",
                classes="error-message",
            )

            # Section 8: All Checks Pass
            yield Static("Scenario 8: All Validations Pass ✅", classes="section-title")
            yield Static(
                "File exists, is readable, isn't too large, symlinks are valid. Safe to open!",
                classes="section-description",
            )
            if valid_file:
                yield FileLink(
                    valid_file,
                    tooltip="✅ All validations passed. Safe to open.",
                )

            # Section 9: Error Recovery Pattern
            yield Static("Section 9: Error Recovery Pattern", classes="section-title")
            yield Static(
                "When opening fails, fallback to another editor or show helpful message:\n\n"
                "try:\n"
                "    open_with_preferred_editor(file)\n"
                "except FileLinkValidationError as e:\n"
                "    show_error_message(e.reason)\n"
                "    if has_fallback_editor():\n"
                "        open_with_fallback_editor(file)",
                classes="section-description",
            )

            # Section 10: Comprehensive Validation
            yield Static("Section 10: Comprehensive Validation", classes="section-title")
            yield Static(
                "Use validate_all() to check everything and get all issues at once. "
                "This is better than early-exit since users see all problems.",
                classes="section-description",
            )
            yield Static(
                "Pattern: Run all validators, collect errors, show them all to user.",
                classes="section-description",
            )
            if valid_file:
                yield FileLink(
                    valid_file,
                    tooltip="Passed: file exists, readable, reasonable size, no symlink issues",
                )

        yield Footer()

    def on_mount(self) -> None:
        """Initialize after mounting."""
        sample_dir = Path("./sample_files")
        if not sample_dir.exists():
            self.notify(
                "Note: ./sample_files not found. Examples use current directory.",
                severity="information",
                timeout=5,
            )


if __name__ == "__main__":
    app = ErrorHandlingApp()
    app.run()
