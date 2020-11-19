"""Module contains some simple validator."""
from pathlib import Path

from prompt_toolkit.validation import ValidationError, Validator


class PathValidator(Validator):
    """Validator class to use for filepath type prompt."""

    def validate(self, document):
        """Test if user input filepath exists."""
        if not Path(document.text).expanduser().exists():
            raise ValidationError(
                message="Input is not a valid path",
                cursor_position=document.cursor_position,
            )


class EmptyInputValidator(Validator):
    """Validator class to detect empty input."""

    def validate(self, document):
        """Check if user input is empty."""
        if not len(document.text) > 0:
            raise ValidationError(
                message="Input cannot be empty",
                cursor_position=document.cursor_position,
            )
