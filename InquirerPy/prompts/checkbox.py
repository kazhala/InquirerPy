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

__all__ = ["CheckboxPrompt"]


class InquirerPyCheckboxControl(InquirerPyUIControl):
    """A UIControl class intended to be used by `prompt_toolkit` window.

    Used to dynamically update the content and indicate the current user selection

    Reference the param definition in `CheckboxPrompt`.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = "%s " % INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = "%s " % INQUIRERPY_EMPTY_HEX_SEQUENCE,
        session_result: Optional[SessionResult] = None,
    ) -> None:
        """Initialise required attributes and call base class."""
        self._pointer = pointer
        self._enabled_symbol = enabled_symbol
        self._disabled_symbol = disabled_symbol
        super().__init__(
            choices=choices,
            default=default,
            session_result=session_result,
            multiselect=True,
        )

    def _format_choices(self) -> None:
        pass

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:checkbox",
                    self._enabled_symbol
                    if choice["enabled"]
                    else self._disabled_symbol,
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
                    self._enabled_symbol
                    if choice["enabled"]
                    else self._disabled_symbol,
                )
            )
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class CheckboxPrompt(BaseListPrompt):
    """A wrapper class around `prompt_toolkit` Application to create a checkbox prompt.

    :param message: Message to display.
    :param choices: List of choices to display.
    :param default: Default value.
    :param style: A dictionary of style.
    :param vi_mode: Use vi kb for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param pointer: The pointer qmark to display.
    :param enabled_symbol: Qmark indicating enabled box.
    :param disabled_symbol: Qmark indicating not selected qmark.
    :param instruction: Instruction to display after the message.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param height: Preferred height of the choice window.
    :param max_height: Max height choice window should reach.
    :param validate: A callable or Validator instance to validate user selection.
    :param invalid_message: Message to display when input is invalid.
    :param keybindings: Custom keybindings to apply.
    :param show_cursor: Display cursor at the end of the prompt.
    :param cycle: Return to top item if hit bottom or vice versa.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = "%s " % INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = "%s " % INQUIRERPY_EMPTY_HEX_SEQUENCE,
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        show_cursor: bool = True,
        cycle: bool = True,
        wrap_lines: bool = True,
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
            amark=amark,
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
            cycle=cycle,
            wrap_lines=wrap_lines,
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
