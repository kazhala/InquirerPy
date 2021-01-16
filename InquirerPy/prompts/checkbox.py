"""Module contains checkbox prompt."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseListPrompt, FakeDocument, InquirerPyUIControl
from InquirerPy.enum import (
    INQUIRERPY_EMPTY_HEX_SEQUENCE,
    INQUIRERPY_FILL_HEX_SEQUENCE,
    INQUIRERPY_POINTER_SEQUENCE,
)
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult


class InquirerPyCheckboxControl(InquirerPyUIControl):
    """A UIControl class intended to be used by `prompt_toolkit` window.

    Used to dynamically update the content and indicate the current user selection

    :param choices: a list of choices to display
    :type choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
    :param default: default value for selection
    :type default: Any
    :param pointer: the pointer to display, indicating current line, default is unicode ">"
    :type pointer: str
    :param enabled_symbol: the qmark to indicate selected choices
    :type enabled_symbol: str
    :param disabled_symbol: the qmark to indicate not selected choices
    :type disabled_symbol: str
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = INQUIRERPY_EMPTY_HEX_SEQUENCE,
        session_result: Optional[SessionResult] = None,
    ) -> None:
        """Initialise required attributes and call base class."""
        self._pointer = "%s " % pointer
        self._enabled_symbol = enabled_symbol
        self._disabled_symbol = disabled_symbol
        super().__init__(
            choices=choices, default=default, session_result=session_result
        )

    def _format_choices(self) -> None:
        for raw_choice, choice in zip(self._raw_choices, self.choices):  # type: ignore
            if isinstance(raw_choice, dict):
                choice["enabled"] = raw_choice.get("enabled", False)
            else:
                choice["enabled"] = False

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:checkbox",
                    "%s " % self._enabled_symbol
                    if choice["enabled"]
                    else "%s " % self._disabled_symbol,
                )
            )
        display_choices.append(("[SetCursorPosition]", ""))
        display_choices.append(("class:pointer", choice["name"]))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("", len(self._pointer) * " "))
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:checkbox",
                    "%s " % self._enabled_symbol
                    if choice["enabled"]
                    else "%s " % self._disabled_symbol,
                )
            )
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class CheckboxPrompt(BaseListPrompt):
    """A wrapper class around `prompt_toolkit` Application to create a checkbox prompt.

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
    :param pointer: the pointer qmark to display
    :type pointer: str
    :param enabled_symbol: qmark indicating enabled box
    :type enabled_symbol: str
    :param disabled_symbol: qmark indicating not selected qmark
    :type disabled_symbol: str
    :param instruction: instruction to display after the message
    :type instruction: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[Any], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
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
        enabled_symbol: str = INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = INQUIRERPY_EMPTY_HEX_SEQUENCE,
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        show_cursor: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyCheckboxControl(
            choices=choices,
            default=default,
            pointer=pointer,
            enabled_symbol=enabled_symbol,
            disabled_symbol=disabled_symbol,
            session_result=session_result,
        )
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
            multiselect=True,
            keybindings=keybindings,
            show_cursor=show_cursor,
            session_result=session_result,
        )

    def _handle_enter(self, event) -> None:
        """Override this method to force empty array result.

        When user does not select anything, exit with empty list.
        """
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
        except ValidationError:
            self._invalid = True
        else:
            self.status["answered"] = True
            self.status["result"] = self.result_name
            event.app.exit(result=self.result_value)
