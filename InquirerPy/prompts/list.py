"""Module contains list prompt."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseListPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    Reference the param definition in `ListPrompt`.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any,
        pointer: str,
        marker: str,
        session_result: Optional[SessionResult],
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self._pointer: str = pointer
        self._marker: str = marker
        super().__init__(
            choices=choices, default=default, session_result=session_result
        )

    def _format_choices(self) -> None:
        pass

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


class ListPrompt(BaseListPrompt):
    """A wrapper class around prompt_toolkit Application to create a list prompt.

    :param message: message to display
    :type message: Union[str, Callable[[SessionResult], str]]
    :param choices: list of choices to display
    :type choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
    :param default: default value
    :type default: Any
    :param style: a dictionary of style
    :type style: InquirerPyStyle
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: bool
    :param qmark: question qmark to display
    :type qmark: str
    :param pointer: the pointer qmark of hovered choice
    :type pointer: str
    :param instruction: instruction to display to user
    :type instruction: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[Any], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
    :param multiselect: enable multiselectiion
    :type multiselect: bool
    :param marker: marker symbol to indicate selected choice in multiselect mode
    :type marker: str
    :param validate: a callable or Validator instance to validate user selection
    :type validate: Union[Callable[[Any], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param keybindings: custom keybindings to apply
    :type keybindings: Dict[str, List[Dict[str, Any]]]
    :param show_cursor: display cursor at the end of the prompt
    :type show_cursor: bool
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        show_cursor: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyListControl(
            choices=choices,
            default=default,
            pointer=pointer,
            marker=marker,
            session_result=session_result,
        )
        self._instruction = instruction
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            instruction=instruction,
            transformer=transformer,
            filter=filter,
            height=height,
            max_height=max_height,
            validate=validate,
            invalid_message=invalid_message,
            multiselect=multiselect,
            keybindings=keybindings,
            show_cursor=show_cursor,
            session_result=session_result,
        )
