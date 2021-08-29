"""Module contains the class to create a rawlist prompt."""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import InquirerPyUIListControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, ListChoices, SessionResult

__all__ = ["RawlistPrompt"]


class InquirerPyRawlistControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.RawlistPrompt`.
    """

    def __init__(
        self,
        choices: ListChoices,
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


class RawlistPrompt(ListPrompt):
    """A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Create a prompt that displays a list of options with index number infront of the choice
    while also create keybinding for all index numbers. Enables user to use number to jump to
    different choices.

    Args:
        message: The question to ask the user.
        choices (ListChoices): List of choices to display.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        vi_mode: Use vim keybinding for the prompt.
        default: The default value. This will affect where the cursor starts from. Should be one of the choice value.
        separator: The separator between the choice index number and the choices.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        pointer: Custom symbol that will be used to indicate the current choice selection.
        instruction: Short instruction to display next to the `message`.
        long_instruction: Long instructions to display at the bottom of the prompt.
        validate: Validation callable or class to validate user input.
        invalid_message: Error message to display when input is invalid.
        transformer: A callable to transform the result that gets printed in the terminal.
            This is visual effect only.
        filter: A callable to filter the result that gets returned.
        height: Preferred height of the choice window.
        max_height: Max height of the choice window.
        multiselect: Enable multi-selection on choices.
        marker: Custom symbol to indicate if a choice is selected.
        marker_pl: Marker place holder when the choice is not selected.
        border: Create border around the choice window.
        keybindings: Custom keybindings to apply. Refer to :ref:`pages/kb:Keybindings`.
        show_cursor: Display cursor at the end of the prompt.
        cycle: Return to top item if hit bottom or vice versa.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        spinner_pattern: List of pattern to display as the spinner.
        spinner_delay: Spinner refresh frequency.
        spinner_text: Loading text to display.
        spinner_enable: Enable spinner when loading choices.
        set_exception_handler: Set exception handler for the event loop.
            If any exception is raised while the `prompt` is visible, the question will enter the `skipped` state and exception will be raised.
            If you have custom exception handler want to set, set this value to `False`.
        session_result: Used for `classic syntax`, ignore this argument.

    Examples:
        >>> result = RawlistPrompt(message="Select one:", choices=[1, 2, 3]).execute()
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: ListChoices,
        default: Any = None,
        separator: str = ") ",
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = " ",
        instruction: str = "",
        long_instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        marker_pl: str = " ",
        border: bool = False,
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
        set_exception_handler: bool = True,
        session_result: SessionResult = None,
    ) -> None:
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
            choices=choices,
            style=style,
            border=border,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            long_instruction=long_instruction,
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
            spinner_enable=spinner_enable,
            spinner_pattern=spinner_pattern,
            spinner_delay=spinner_delay,
            spinner_text=spinner_text,
            set_exception_handler=set_exception_handler,
            session_result=session_result,
        )

    def _choices_callback(self, _) -> None:
        """Override this method to apply custom keybindings.

        Needs to creat these kb in the callback due to `after_render`
        retrieve the choices asynchronously.

        Check if fetched choices exceed the limit of 9, raise
        InvalidArgument exception.
        """

        def keybinding_factory(choice):
            @self._register_kb(str(choice["display_index"]))
            def keybinding(_) -> None:
                self.content_control.selected_choice_index = int(choice["actual_index"])

            return keybinding

        if self.content_control.choice_count >= 10:
            raise InvalidArgument("rawlist argument choices cannot exceed length of 9")

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
