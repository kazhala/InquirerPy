"""Module contains some simple validator."""
from pathlib import Path

from prompt_toolkit.validation import ValidationError, Validator


class PathValidator(Validator):
    def validate(self, document):
        if not Path(document.text).expanduser().exists():
            raise ValidationError(
                message="Input is not a valid path",
                cursor_position=document.cursor_position,
            )
