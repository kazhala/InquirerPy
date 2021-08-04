"""Module contains list prompt."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseListPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["ListPrompt"]


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
        multiselect: bool,
        marker_pl: str = " ",
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self._pointer: str = pointer
        self._marker: str = marker
        self._marker_pl: str = marker_pl
        super().__init__(
            choices=choices,
            default=default,
            session_result=session_result,
            multiselect=multiselect,
        )

    def _format_choices(self) -> None:
        pass

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            (
                "class:marker",
                self._marker if choice["enabled"] else self._marker_pl,
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
                self._marker if choice["enabled"] else self._marker_pl,
            )
        )
        if not isinstance(choice["value"], Separator):
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class ListPrompt(BaseListPrompt):
    """A wrapper class around prompt_toolkit Application to create a list prompt.

    :param message: Message to display.
    :param choices: List of choices to display.
    :param default: The default value.
    :param style: Style config in dictionary form.
    :param vi_mode: Use vi keybindings for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param pointer: The pointer qmark of hovered choice.
    :param instruction: Instruction to display to user.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param height: Preferred height of the choice window.
    :param max_height: Max height choice window should reach.
    :param multiselect: Enable multiselectiion.
    :param marker: Marker symbol to indicate selected choice in multiselect mode.
    :param marker_pl: Marker place holder for non selected choices.
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
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        marker_pl: str = " ",
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        show_cursor: bool = True,
        cycle: bool = True,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyListControl(
            choices=choices,
            default=default,
            pointer=pointer,
            marker=marker,
            session_result=session_result,
            multiselect=multiselect,
            marker_pl=marker_pl,
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
            multiselect=multiselect,
            keybindings=keybindings,
            show_cursor=show_cursor,
            cycle=cycle,
            wrap_lines=wrap_lines,
            session_result=session_result,
        )
