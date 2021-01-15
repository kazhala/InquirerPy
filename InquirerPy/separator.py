"""Module contains Separator class."""


class Separator:
    """Can be used between choices to separete list content.

    :param content: the content to display as the separator
    :type content: str
    """

    def __init__(self, line: str = 15 * "-") -> None:
        """Initialise the content."""
        self.line = line

    def __str__(self) -> str:
        """Call str function on Separator."""
        return self.line
