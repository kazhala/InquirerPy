"""Module contains some simple validator."""
import re
from pathlib import Path

from prompt_toolkit.validation import ValidationError, Validator

__all__ = [
    "PathValidator",
    "EmptyInputValidator",
    "PasswordValidator",
    "NumberValidator",
]


class NumberValidator(Validator):
    """Validator class to validate if input is a number.

    :param float_allowed: allow float input
    :type float_allowed: bool
    :param message: error message to display
    :type message: str
    """

    def __init__(
        self, message: str = "Input should be number", float_allowed: bool = False
    ) -> None:
        """Set invalid message and determine float."""
        self.message = message
        self.float_allowed = float_allowed

    def validate(self, document) -> None:
        """Check if user input is a valid number."""
        try:
            if self.float_allowed:
                float(document.text)
            else:
                int(document.text)
        except ValueError:
            raise ValidationError(
                message=self.message, cursor_position=document.cursor_position
            )


class PathValidator(Validator):
    """Validator class to validate if input is a valid filepath.

    :param message: error message to display
    :type message: str
    """

    def __init__(
        self,
        message: str = "Input is not a valid path",
        is_file: bool = False,
        is_dir: bool = False,
    ) -> None:
        """Set invalid message and check condition."""
        self.message = message
        self.is_file = is_file
        self.is_dir = is_dir

    def validate(self, document) -> None:
        """Check if user input filepath exists based on condition."""
        path = Path(document.text).expanduser()
        if self.is_file and not path.is_file():
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )
        elif self.is_dir and not path.is_dir():
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )
        elif not path.exists():
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )


class EmptyInputValidator(Validator):
    """Validator class to validate empty input.

    :param message: error message to display
    :type message: str
    """

    def __init__(self, message: str = "Input cannot be empty") -> None:
        """Set invalid message."""
        self.message = message

    def validate(self, document) -> None:
        """Check if user input is empty."""
        if not len(document.text) > 0:
            raise ValidationError(
                message=self.message,
                cursor_position=document.cursor_position,
            )


class PasswordValidator(Validator):
    """Validator class to check password compliance.

    :param message: error message to display
    :type message: str
    :param length: the minimum length of the password
    :type length: Optional[int]
    :param cap: password include at least one cap
    :type cap: bool
    :param special: password include at least one special char "@$!%*#?&"
    :type special: bool
    :param number: password include at least one number
    :type number: bool
    """

    def __init__(
        self,
        message: str = "Input is not a valid pattern",
        length: int = None,
        cap: bool = False,
        special: bool = False,
        number: bool = False,
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

    def validate(self, document) -> None:
        """Check if user input passes the password constraint."""
        if not self.re.match(document.text):
            raise ValidationError(
                message=self.message, cursor_position=document.cursor_position
            )
