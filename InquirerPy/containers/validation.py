"""Module contains :class:`.ValidationWindow` which can be used to display error."""

from prompt_toolkit.filters.base import FilterOrBool
from prompt_toolkit.formatted_text.base import AnyFormattedText
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl


class ValidationWindow(ConditionalContainer):
    """Conditional `prompt_toolkit` :class:`~prompt_toolkit.layout.Window` that displays error.

    Args:
        invalid_message: Error message to display when error occured.
        filter: Condition to display the error window.
    """

    def __init__(
        self, invalid_message: AnyFormattedText, filter: FilterOrBool, **kwargs
    ) -> None:
        super().__init__(
            Window(
                FormattedTextControl(invalid_message), dont_extend_height=True, **kwargs
            ),
            filter=filter,
        )
