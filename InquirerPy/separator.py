"""Module contains the :class:`.Separator` class."""


class Separator:
    """A non selectable choice that can be used as part of the choices argument in list type prompts.

    It can be used to create some visual separations between choices in list type prompts.

    Args:
        line: Content to display as the separator.

    Example:
        >>> from InquirerPy import inquirer
        >>> choices = [1, 2, Separator(), 3]
        >>> inquirer.select(message="", choices=choices)
    """

    def __init__(self, line: str = 15 * "-") -> None:
        self._line = line

    def __str__(self) -> str:
        """Create string representation of `Separator`."""
        return self._line
