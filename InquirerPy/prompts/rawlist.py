"""Module contains the rawlist prompt."""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseListPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["RawlistPrompt"]


class InquirerPyRawlistControl(InquirerPyUIControl):
    """A content control instance intended to used by `prompt_tool_kit` Window.

    All parameter types and purposes, reference `RawlistPrompt`.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any,
        pointer: str,
        separator: str,
        marker: str,
        session_result: Optional[SessionResult],
        multiselect: bool,
        marker_pl: str = " ",
    ) -> None:
        self._pointer = pointer
        self._separator = separator
        self._marker = marker
        self._marker_pl = marker_pl
        super().__init__(
            choices=choices,
            default=default,
            session_result=session_result,
            multiselect=multiselect,
        )

    def _format_choices(self) -> None:
        separator_count = 0
        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                separator_count += 1
                continue
            choice["display_index"] = index + 1 - separator_count
            choice["actual_index"] = index

        if self.choices:
            first_valid_choice_index = 0
            while isinstance(
                self.choices[first_valid_choice_index]["value"], Separator
            ):
                first_valid_choice_index += 1
            if self.selected_choice_index == first_valid_choice_index:
                for choice in self.choices:
                    if isinstance(choice["value"], Separator):
                        continue
                    if choice["display_index"] == self._default:
                        self.selected_choice_index = choice["actual_index"]
                        break

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            (
                "class:marker",
                self._marker if choice["enabled"] else self._marker_pl,
            )
        )
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:pointer",
                    "%s%s" % (str(choice["display_index"]), self._separator),
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
            display_choices.append(
                ("", "%s%s" % (str(choice["display_index"]), self._separator))
            )
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class RawlistPrompt(BaseListPrompt):
    """Used to create a rawlist prompt where user can use number to jump to items.

    :param message: Message to display as question
    :param choices: List of choices available for selection.
    :param default: Default value.
    :param separator: The separator between the index number and the choices.
        e.g. default separator is ")"
            1) whatever
            2) whatever
    :param style: Style for the prompt.
    :param vi_mode: Use vi kb for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param pointer: Pointer qmark to display.
    :param instruction: Instruction to display at the end of the prompt.
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
        separator: str = ") ",
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = " ",
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
        """Construct content control and initialise the application while also apply keybindings."""
        self.content_control = InquirerPyRawlistControl(
            choices=choices,
            default=default,
            pointer=pointer,
            separator=separator,
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
            multiselect=multiselect,
            validate=validate,
            invalid_message=invalid_message,
            keybindings=keybindings,
            show_cursor=show_cursor,
            cycle=cycle,
            wrap_lines=wrap_lines,
            session_result=session_result,
        )

    def _after_render(self, application) -> None:
        """Override this method to apply custom keybindings.

        Since `self.content_control.choices` may not exists before
        `Application` is created if its a callable, create these
        chocies based keybindings in the after_render call.

        Check if fetched choices exceed the limit of 9, raise
        InvalidArgument exception.
        """
        if not self._rendered:
            super()._after_render(application)
            if self.content_control.choice_count >= 10:
                raise InvalidArgument("rawlist choices cannot exceed 9.")

            def keybinding_factory(choice):
                @self._register_kb(str(choice["display_index"]))
                def keybinding(_) -> None:
                    self.content_control.selected_choice_index = int(
                        choice["actual_index"]
                    )

                return keybinding

            for choice in self.content_control.choices:
                if not isinstance(choice["value"], Separator):
                    keybinding_factory(choice)

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Overriding this method to allow multiple formatted class to be displayed.
        """
        display_message = super()._get_prompt_message()
        if not self.status["answered"] and self.content_control.choices:
            display_message.append(
                ("class:input", str(self.content_control.selection["display_index"]))
            )
        return display_message
