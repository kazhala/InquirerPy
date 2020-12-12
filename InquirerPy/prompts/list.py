"""Module contains list prompt."""

from typing import Any, Dict, List, Literal, Tuple, Union

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    :param choices: a list of choices to display
    :type choices: List[Union[Any, Dict[str, Any]]]
    :param default: default selection
    :type default: Any
    :param pointer: the pointer char to display, default is unicode ">"
    :type pointer: str
    """

    def __init__(
        self,
        choices: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self.pointer: str = "%s " % pointer
        super().__init__(choices=choices, default=default)

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self.pointer))
        display_choices.append(("class:pointer", choice["name"]))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("", len(self.pointer) * " "))
        display_choices.append(("", choice["name"]))
        return display_choices


class ListPrompt(BaseComplexPrompt):
    """A wrapper class around prompt_toolkit Application to create a list prompt.

    :param message: message to display
    :type message: str
    :param choices: list of choices to display
    :type choices: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param style: a dictionary of style
    :type style: Dict[str, str]
    :param editing_mode: editing_mode of the prompt
    :type editing_mode: Literal["emacs", "default", "vim"]
    :param qmark: question qmark to display
    :type qmark: str
    :param pointer: the pointer qmark of hovered choice
    :type pointer: str
    :param instruction: instruction to display to user
    :type instruction: str
    """

    def __init__(
        self,
        message: str,
        choices: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        qmark: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyListControl(choices, default, pointer)
        self._instruction = instruction
        super().__init__(message, style, editing_mode, qmark, instruction)
