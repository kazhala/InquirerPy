"""Module contains list prompt."""

from typing import Any, Callable, Dict, List, Literal, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.separator import Separator


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    Reference the param definition in `ListPrompt`.
    """

    def __init__(
        self,
        choices: List[Union[Any, Dict[str, Any]]],
        default: Any,
        pointer: str,
        multiselect: bool,
        marker: str,
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self._pointer: str = pointer
        self._marker: str = marker
        self._multiselect = multiselect
        super().__init__(choices=choices, default=default)

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            (
                "class:marker",
                self._marker if choice["enabled"] else " ",
            )
        )
        display_choices.append(("[SetCursorPosition]", ""))
        display_choices.append(("class:pointer", choice["name"]))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("", len(self._pointer) * " "))
        display_choices.append(
            (
                "class:marker",
                self._marker if choice["enabled"] else " ",
            )
        )
        if not isinstance(choice["value"], Separator):
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
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
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
    :param multiselect: enable multiselectiion
    :type multiselect: bool
    :param marker: marker symbol to indicate selected choice in multiselect mode
    :type marker: str
    :param validate: a callable or Validator instance to validate user selection
    :type validate: Union[Callable[[str], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
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
        transformer: Callable = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyListControl(
            choices=choices,
            default=default,
            pointer=pointer,
            multiselect=multiselect,
            marker=marker,
        )
        self._instruction = instruction
        super().__init__(
            message=message,
            style=style,
            editing_mode=editing_mode,
            qmark=qmark,
            instruction=instruction,
            transformer=transformer,
            height=height,
            max_height=max_height,
            validate=validate,
            invalid_message=invalid_message,
            multiselect=multiselect,
        )
