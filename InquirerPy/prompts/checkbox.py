"""Module contains the class to create a checkbox prompt."""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import FakeDocument, InquirerPyUIListControl
from InquirerPy.enum import (
    INQUIRERPY_EMPTY_HEX_SEQUENCE,
    INQUIRERPY_FILL_HEX_SEQUENCE,
    INQUIRERPY_POINTER_SEQUENCE,
)
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyListChoices,
    InquirerPySessionResult,
    InquirerPyStyle,
)

__all__ = ["CheckboxPrompt"]


class InquirerPyCheckboxControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.CheckboxPrompt`.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        default: Any = None,
        pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = "%s " % INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = "%s " % INQUIRERPY_EMPTY_HEX_SEQUENCE,
        session_result: Optional[InquirerPySessionResult] = None,
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


class CheckboxPrompt(ListPrompt):
    """A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Create a prompt which displays a list of checkboxes. User can toggle
    on/off on each checkbox.

    Args:
        message: The question to ask the user.
        choices (InquirerPyListChoices): List of choices to display.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        vi_mode: Use vim keybinding for the prompt.
        default: The default value. This will affect where the cursor starts from. Should be one of the choice value.
        separator: The separator between the choice letter and the choices.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        pointer: Custom symbol that will be used to indicate the current choice selection.
        enabled_symbol: Custom symbol which indicate the checkbox is ticked.
        disabled_symbol: Custom symbol which indicate the checkbox is not ticked.
        border: Create border around the choice window.
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
        session_result: Used for `classic syntax`, ignore this parameter.

    Examples:
        >>> result = CheckboxPrompt(message="Select:", choices=[1, 2, 3]).execute()
    """

    def __init__(
        self,
        message: Union[str, Callable[[InquirerPySessionResult], str]],
        choices: InquirerPyListChoices,
        default: Any = None,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = "%s " % INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = "%s " % INQUIRERPY_EMPTY_HEX_SEQUENCE,
        border: bool = False,
        instruction: str = "",
        long_instruction: str = "",
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
        spinner_enable: bool = False,
        spinner_pattern: List[str] = None,
        spinner_text: str = "",
        spinner_delay: float = 0.1,
        set_exception_handler: bool = True,
        session_result: InquirerPySessionResult = None,
    ) -> None:
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
            validate=validate,
            invalid_message=invalid_message,
            multiselect=True,
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

    def _handle_enter(self, event) -> None:
        """Override this method to force empty array result.

        When user does not select anything, exit with empty list.

        Args:
            event: Keypress event.
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
