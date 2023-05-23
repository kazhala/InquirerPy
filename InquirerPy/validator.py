"""Module contains pre-built validators."""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from prompt_toolkit.validation import ValidationError, Validator

__all__ = [
    "PathValidator",
    "EmptyInputValidator",
    "PasswordValidator",
    "NumberValidator",
    "DateValidator"
]


class NumberValidator(Validator):
    """:class:`~prompt_toolkit.validation.Validator` to validate if input is a number.

    Args:
        message: Error message to display in the validatation toolbar when validation failed.
        float_allowed: Allow input to contain floating number (with decimal).
    """

    def __init__(
        self, message: str = "Input should be a number", float_allowed: bool = False
    ) -> None:
        self._message = message
        self._float_allowed = float_allowed

    def validate(self, document) -> None:
        """Check if user input is a valid number.

        This method is used internally by `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_.

        See Also:
            https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html?highlight=validator#input-validation
        """
        try:
            if self._float_allowed:
                float(document.text)
            else:
                int(document.text)
        except ValueError:
            raise ValidationError(
                message=self._message, cursor_position=document.cursor_position
            )


class PathValidator(Validator):
    """:class:`~prompt_toolkit.validation.Validator` to validate if input is a valid filepath on the system.

    Args:
        message: Error message to display in the validatation toolbar when validation failed.
        is_file: Explicitly check if the input is a valid file on the system.
        is_dir: Explicitly check if the input is a valid directory/folder on the system.
    """

    def __init__(
        self,
        message: str = "Input is not a valid path",
        is_file: bool = False,
        is_dir: bool = False,
    ) -> None:
        self._message = message
        self._is_file = is_file
        self._is_dir = is_dir

    def validate(self, document) -> None:
        """Check if user input is a filepath that exists on the system based on conditions.

        This method is used internally by `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_.

        See Also:
            https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html?highlight=validator#input-validation
        """
        path = Path(document.text).expanduser()
        if self._is_file and not path.is_file():
            raise ValidationError(
                message=self._message,
                cursor_position=document.cursor_position,
            )
        elif self._is_dir and not path.is_dir():
            raise ValidationError(
                message=self._message,
                cursor_position=document.cursor_position,
            )
        elif not path.exists():
            raise ValidationError(
                message=self._message,
                cursor_position=document.cursor_position,
            )


class EmptyInputValidator(Validator):
    """:class:`~prompt_toolkit.validation.Validator` to validate if the input is empty.

    Args:
        message: Error message to display in the validatation toolbar when validation failed.
    """

    def __init__(self, message: str = "Input cannot be empty") -> None:
        self._message = message

    def validate(self, document) -> None:
        """Check if user input is empty.

        This method is used internally by `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_.

        See Also:
            https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html?highlight=validator#input-validation
        """
        if not len(document.text) > 0:
            raise ValidationError(
                message=self._message,
                cursor_position=document.cursor_position,
            )


class PasswordValidator(Validator):
    """:class:`~prompt_toolkit.validation.Validator` to validate password compliance.

    Args:
        message: Error message to display in the validatation toolbar when validation failed.
        length: The minimum length of the password.
        cap: Password should include at least one capital letter.
        special: Password should include at least one special char "@$!%*#?&".
        number: Password should include at least one number.
    """

    def __init__(
        self,
        message: str = "Input is not compliant with the password constraints",
        length: Optional[int] = None,
        cap: bool = False,
        special: bool = False,
        number: bool = False,
    ) -> None:
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
        self._re = re.compile(password_pattern)
        self._message = message

    def validate(self, document) -> None:
        """Check if user input is compliant with the specified password constraints.

        This method is used internally by `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_.

        See Also:
            https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html?highlight=validator#input-validation
        """
        if not self._re.match(document.text):
            raise ValidationError(
                message=self._message, cursor_position=document.cursor_position
            )


class DateValidator(Validator):
    """:class:`~prompt_toolkit.validation.Validator` to validate if input is a valid date.

    Args:
        message: Error message to display in the validatation toolbar when validation failed.
        format: Specify the desired date format.
    """

    def __init__(
        self,
        message: str = "Invalid date format",
        formats: list[str] = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"],
    ) -> None:
        self._message = message
        self._formats = formats

    def validate(self, input_date) -> None:
        """Check if the user's date input is valid and well-formatted.

        This method is used internally by `prompt_toolkit <https://python-prompt-toolkit.readthedocs.io/en/master/>`_.

        See Also:
            https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html?highlight=validator#input-validation

        """

        for form in self._formats:
            try:
                return datetime.strptime(input_date.text, form)
            except ValueError:
                continue

        raise ValidationError(
            message=self._message,
            cursor_position=input_date.cursor_position,
        )