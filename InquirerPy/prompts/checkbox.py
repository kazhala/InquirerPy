"""Module contains the class to create a checkbox prompt."""
from typing import Any, Callable, List, Optional, Tuple, Union

from prompt_toolkit.validation import ValidationError

from InquirerPy.base import FakeDocument, InquirerPyUIListControl
from InquirerPy.enum import (
    INQUIRERPY_EMPTY_CIRCLE_SEQUENCE,
    INQUIRERPY_FILL_CIRCLE_SEQUENCE,
    INQUIRERPY_POINTER_SEQUENCE,
)
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyKeybindings,
    InquirerPyListChoices,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)

__all__ = ["CheckboxPrompt"]


class InquirerPyCheckboxControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.CheckboxPrompt`.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        default: Any,
        pointer: str,
        enabled_symbol: str,
        disabled_symbol: str,
        session_result: Optional[InquirerPySessionResult],
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
        if self._pointer:
            display_choices.append(("", " "))
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:checkbox",
                    self._enabled_symbol
                    if choice["enabled"]
                    else self._disabled_symbol,
                )
            )
            if self._enabled_symbol and self._disabled_symbol:
                display_choices.append(("", " "))
        display_choices.append(("[SetCursorPosition]", ""))
        display_choices.append(("class:pointer", choice["name"]))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("", len(self._pointer) * " "))
        if self._pointer:
            display_choices.append(("", " "))
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                (
                    "class:checkbox",
                    self._enabled_symbol
                    if choice["enabled"]
                    else self._disabled_symbol,
                )
            )
            if self._enabled_symbol and self._disabled_symbol:
                display_choices.append(("", " "))
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class CheckboxPrompt(ListPrompt):
    """Create a prompt which displays a list of checkboxes to toggle.

    A wrapper class around :class:`~prompt_toolkit.application.Application`.

    User can toggle on/off on each checkbox.

    Works very similar to :class:`~InquirerPy.prompts.list.ListPrompt` with `multiselect` enabled,
    the main difference is visual/UI and also when not toggling anything, the result will be empty.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        choices: List of choices to display and select.
            Refer to :ref:`pages/dynamic:choices` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default value of the prompt.
            This will be used to determine which choice is highlighted (current selection),
            The default value should be the value of one of the choices.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        separator: Separator symbol. Custom symbol that will be used as a separator between the choice index number and the choices.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        pointer: Pointer symbol. Customer symbol that will be used to indicate the current choice selection.
        enabled_symbol: Checkbox ticked symbol. Custom symbol which indicate the checkbox is ticked.
        disabled_symbol: Checkbox not ticked symbol. Custom symbol which indicate the checkbox is not ticked.
        instruction: Short instruction to display next to the question.
        long_instruction: Long instructions to display at the bottom of the prompt.
        validate: Add validation to user input.
            The main use case for this prompt would be when `multiselect` is True, you can enforce a min/max selection.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        invalid_message: Error message to display when user input is invalid.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        transformer: A function which performs additional transformation on the value that gets printed to the terminal.
            Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:transformer` documentation for more details.
        filter: A function which performs additional transformation on the result.
            This affects the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:filter` documentation for more details.
        height: Preferred height of the prompt.
            Refer to :ref:`pages/height:Height` documentation for more details.
        max_height: Max height of the prompt.
            Refer to :ref:`pages/height:Height` documentation for more details.
        border: Create border around the choice window.
        keybindings: Customise the builtin keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more details.
        show_cursor: Display cursor at the end of the prompt.
            Set to False to hide the cursor.
        cycle: Return to top item if hit bottom during navigation or vice versa.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.checkbox(message="Select:", choices=[1, 2, 3]).execute()
        >>> print(result)
        [1]
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        choices: InquirerPyListChoices,
        default: Any = None,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = INQUIRERPY_FILL_CIRCLE_SEQUENCE,
        disabled_symbol: str = INQUIRERPY_EMPTY_CIRCLE_SEQUENCE,
        border: bool = False,
        instruction: str = "",
        long_instruction: str = "",
        transformer: Optional[Callable[[Any], Any]] = None,
        filter: Optional[Callable[[Any], Any]] = None,
        height: Optional[Union[int, str]] = None,
        max_height: Optional[Union[int, str]] = None,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        keybindings: Optional[InquirerPyKeybindings] = None,
        show_cursor: bool = True,
        cycle: bool = True,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
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
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
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
