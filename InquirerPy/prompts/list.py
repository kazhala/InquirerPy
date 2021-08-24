"""Module contains list prompt."""

import shutil
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.application.application import Application
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    FloatContainer,
    HSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import InquirerPyUIControl
from InquirerPy.base.complex import FakeDocument
from InquirerPy.base.list import BaseListPrompt
from InquirerPy.containers.message import MessageWindow
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyStyle,
    ListChoices,
    SessionResult,
    calculate_height,
)

__all__ = ["ListPrompt"]


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    Reference the param definition in `ListPrompt`.
    """

    def __init__(
        self,
        choices: ListChoices,
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
    :param spinner_enable: Enable spinner while loading choices.
    :param spinner_pattern: List of pattern to display as the spinner.
    :param spinner_delay: Spinner refresh frequency.
    :param spinner_text: Loading text to display.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: ListChoices,
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
        spinner_enable: bool = False,
        spinner_pattern: List[str] = None,
        spinner_text: str = "",
        spinner_delay: float = 0.1,
        session_result: SessionResult = None,
    ) -> None:
        if not hasattr(self, "_content_control"):
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
            validate=validate,
            invalid_message=invalid_message,
            multiselect=multiselect,
            keybindings=keybindings,
            cycle=cycle,
            wrap_lines=wrap_lines,
            spinner_enable=spinner_enable,
            spinner_pattern=spinner_pattern,
            spinner_delay=spinner_delay,
            spinner_text=spinner_text,
            session_result=session_result,
        )
        self._show_cursor = show_cursor
        self._dimmension_height, self._dimmension_max_height = calculate_height(
            height,
            max_height,
            wrap_lines_offset=self.wrap_lines_offset,
        )

        self.layout = FloatContainer(
            content=HSplit(
                [
                    MessageWindow(
                        message=self._get_prompt_message_with_cursor
                        if self._show_cursor
                        else self._get_prompt_message,
                        filter=~self._is_loading | ~self._is_spinner_enable,
                        wrap_lines=self._wrap_lines,
                        show_cursor=self._show_cursor,
                    ),
                    self._spinner,
                    ConditionalContainer(
                        Window(
                            content=self.content_control,
                            height=Dimension(
                                max=self._dimmension_max_height,
                                preferred=self._dimmension_height,
                            ),
                            dont_extend_height=True,
                        ),
                        filter=~IsDone() & ~self._is_loading,
                    ),
                ]
            ),
            floats=[
                Float(
                    content=ConditionalContainer(
                        Window(
                            FormattedTextControl(
                                [
                                    (
                                        "class:validation-toolbar",
                                        self._invalid_message,
                                    )
                                ]
                            ),
                            dont_extend_height=True,
                        ),
                        filter=self._is_invalid & ~IsDone(),
                    ),
                    left=0,
                    bottom=0,
                )
            ],
        )

        self.application = Application(
            layout=Layout(self.layout),
            style=self._style,
            key_bindings=self._kb,
            after_render=self._after_render,
        )

    def _get_prompt_message_with_cursor(self) -> List[Tuple[str, str]]:
        """Obtain the prompt message to display.

        Introduced a new method instead of using the `_get_prompt_message`
        due to `expand` and `rawlist` make changes after calling `super()._get_prompt_message()`.

        This ensures that cursor is always at the end of the window no matter
        when the changes is made to the `_get_prompt_message`.
        """
        message = self._get_prompt_message()
        message.append(("[SetCursorPosition]", ""))
        message.append(("", " "))  # [SetCursorPosition] require char behind it
        return message

    def _toggle_choice(self) -> None:
        """Toggle the `enabled` status of the choice."""
        self.content_control.selection["enabled"] = not self.content_control.selection[
            "enabled"
        ]

    def _toggle_all(self, value: bool = None) -> None:
        """Toggle all choice `enabled` status.

        :param value: Sepcify a value to toggle.
        """
        for choice in self.content_control.choices:
            if isinstance(choice["value"], Separator):
                continue
            choice["enabled"] = value if value else not choice["enabled"]

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up."""
        while True:
            cap = super()._handle_up()
            if not isinstance(self.content_control.selection["value"], Separator):
                break
            else:
                if cap and not self._cycle:
                    self._handle_down()
                    break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down."""
        while True:
            cap = super()._handle_down()
            if not isinstance(self.content_control.selection["value"], Separator):
                break
            else:
                if cap and not self._cycle:
                    self._handle_up()
                    break

    def _handle_enter(self, event) -> None:
        """Handle the event when user hit Enter key.

        * Set the state to answered for an update to the prompt display.
        * Set the result to user selected choice's name for display purpose.
        * Let the app exit with the user selected choice's value and return the actual value back to resolver.

        In multiselect scenario, if nothing is selected, return the current highlighted choice.
        """
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
        except ValidationError:
            self._invalid = True
        else:
            self.status["answered"] = True
            if self._multiselect and not self.selected_choices:
                self.status["result"] = [self.content_control.selection["name"]]
                event.app.exit(result=[self.content_control.selection["value"]])
            else:
                self.status["result"] = self.result_name
                event.app.exit(result=self.result_value)

    @property
    def wrap_lines_offset(self) -> int:
        """Get extra offset due to line wrapping.

        Overriding it to count the cursor as well.

        :return: Extra offset.
        """
        if not self._wrap_lines:
            return 0
        total_message_length = self.total_message_length
        if self._show_cursor:
            total_message_length += 1
        term_width, _ = shutil.get_terminal_size()
        return total_message_length // term_width
