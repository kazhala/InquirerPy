"""Module contains list prompt."""

from typing import Any, Dict, List, Literal, Tuple, Union

from InquirerPy.base import (
    BaseComplexPrompt,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    :param options: a list of options to display
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default selection
    :type default: Any
    :param pointer: the pointer char to display, default is unicode ">"
    :type pointer: str
    """

    def __init__(
        self,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self.pointer: str = pointer
        super().__init__(options=options, default=default)

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_options = []
        display_options.append(("class:pointer", " %s " % self.pointer))
        display_options.append(("[SetCursorPosition]", ""))
        display_options.append(("class:pointer", str(option["name"])))
        return display_options

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_options = []
        display_options.append(("", "   "))
        display_options.append(("", str(option["name"])))
        return display_options


class ListPrompt(BaseComplexPrompt):
    """A wrapper class around prompt_toolkit Application to create a list prompt.

    :param message: message to display
    :type message: str
    :param options: list of options to display
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param style: a dictionary of style
    :type style: Dict[str, str]
    :param editing_mode: editing_mode of the prompt
    :type editing_mode: Literal["emacs", "default", "vim"]
    :param symbol: question symbol to display
    :type symbol: str
    :param pointer: the pointer symbol of hovered option
    :type pointer: str
    :param instruction: instruction to display to user
    :type instruction: str
    """

    def __init__(
        self,
        message: str,
        options: List[Union[Any, Dict[str, Any]]],
        style: Dict[str, str],
        default: Any = None,
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        symbol: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
    ) -> None:
        """Initialise the content_control and create Application."""
        self.pointer = pointer
        self.content_control = InquirerPyListControl(options, default, pointer)
        self._instruction = instruction
        super().__init__(message, style, editing_mode, symbol)

    def handle_enter(self, event) -> None:
        """Handle the event when user hit Enter."""
        self.status["answered"] = True
        self.status["result"] = self.content_control.selection["name"]
        event.app.exit(result=self.content_control.selection["value"])

    @property
    def instruction(self) -> str:
        """Get the instruction to print."""
        return self._instruction
