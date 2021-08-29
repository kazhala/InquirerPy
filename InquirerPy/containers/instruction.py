"""Module contains :class:`.InstructionWindow` which can be used to display long instructions."""

from typing import TYPE_CHECKING

from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl

if TYPE_CHECKING:
    from prompt_toolkit.filters.base import FilterOrBool
    from prompt_toolkit.formatted_text.base import AnyFormattedText


class InstructionWindow(ConditionalContainer):
    """Conditional `prompt_toolkit` :class:`~prompt_toolkit.layout.Window` that displays long instructions.

    Args:
        message: Long instructions to display.
        filter: Condition to display the instruction window.
    """

    def __init__(self, message: str, filter: "FilterOrBool", wrap_lines: bool) -> None:
        self._message = message
        super().__init__(
            Window(
                FormattedTextControl(text=self._get_message),
                dont_extend_height=True,
                wrap_lines=wrap_lines,
            ),
            filter=filter,
        )

    def _get_message(self) -> "AnyFormattedText":
        """Get long instruction to display.

        Returns:
            FormattedText in list of tuple format.
        """
        return [("class:instruction", self._message)]
