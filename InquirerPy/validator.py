"""Module contains some simple validator."""
from pathlib import Path
import re
from typing import Optional

from prompt_toolkit.validation import ValidationError, Validator

__all__ = ["PathValidator", "EmptyInputValidator", "PasswordValidator"]


class PathValidator(Validator):
    """Validator class to validate if input is a valid filepath.

    :param message: error message to display
    :type message: str
    """

    def __init__(self, message: str = "Input is not a valid path"):
        """Set invalid message."""
        self.message = message

    def validate(self, document):
        """Check if user input filepath exists."""
        if not Path(document.text).expanduser().exists():
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )


class EmptyInputValidator(Validator):
    """Validator class to validate empty input.

    :param message: error message to display
    :type message: str
    """

    def __init__(self, message: str = "Input cannot be empty"):
        """Set invalid message."""
        self.message = message

    def validate(self, document):
        """Check if user input is empty."""
        if not len(document.text) > 0:
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )


class PasswordValidator(Validator):
    """Validator class to check password compliance.

    :param length: the minimum length of the password
    :type length: Optional[int]
    :param cap: password include at least one cap
    :type cap: bool
    :param special: password include at least one special char "@$!%*#?&"
    :type special: bool
    :param number: password include at least one number
    :type number: bool
    :param message: error message to display
    :type message: str
    """

    def __init__(
        self,
        length: Optional[int] = None,
        cap: bool = False,
        special: bool = False,
        number: bool = False,
        message: str = "Input is not a valid pattern",
    ) -> None:
        """Set regex pattern and invalid message."""
        password_pattern = r"^"
        if cap:
            password_pattern += r"(?=.*[A-Z])"
        if special:
            password_pattern += r"(?=.*[@$!%*#?&])"
        if number:
            password_pattern += r"(?=.*[0-9])"
        password_pattern += r"."
        if length:
            password_pattern += r"{%s,}" % length
        else:
            password_pattern += r"*"
        password_pattern += r"$"
        self.re = re.compile(password_pattern)
        self.message = message

    def validate(self, document):
        """Check if user input passes the password constraint."""
        if not self.re.match(document.text):
            raise ValidationError(
                message=self.message, cursor_position=document.cursor_position
            )
