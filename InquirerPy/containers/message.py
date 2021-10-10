"""Module contains the main message window :class:`~prompt_toolkit.container.Container`."""

from typing import TYPE_CHECKING

from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension

if TYPE_CHECKING:
    from prompt_toolkit.filters.base import FilterOrBool
    from prompt_toolkit.formatted_text.base import AnyFormattedText


class MessageWindow(ConditionalContainer):
    """Main window to display question to the user.

    Args:
        message: The message to display in the terminal.
        filter: Condition that this message window should be displayed.
            Use a loading condition to only display this window while its not loading.
        wrap_lines: Enable line wrapping if the message is too long.
        show_cursor: Display cursor.
    """

    def __init__(
        self,
        message: "AnyFormattedText",
        filter: "FilterOrBool",
        wrap_lines: bool = True,
        show_cursor: bool = True,
        **kwargs
    ) -> None:
        super().__init__(
            content=Window(
                height=LayoutDimension.exact(1) if not wrap_lines else None,
                content=FormattedTextControl(message, show_cursor=show_cursor),
                wrap_lines=wrap_lines,
                dont_extend_height=True,
                **kwargs
            ),
            filter=filter,
        )
