"""Module contains the class to create a rawlist prompt."""
from typing import Any, Callable, List, Optional, Tuple, Union

from InquirerPy.base import InquirerPyUIListControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyListChoices,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)

__all__ = ["RawlistPrompt"]


class InquirerPyRawlistControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.RawlistPrompt`.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        default: Any,
        pointer: str,
        separator: str,
        marker: str,
        session_result: Optional[InquirerPySessionResult],
        multiselect: bool,
        marker_pl: str,
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
    """Create a prompt that displays a list of choices with index number as shortcuts.

    A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Each choice will have an index number infront of them with keybinding created for that index number.
    Enables user to use number to jump to different choices using number.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        choices: List of choices to display and select.
            Refer to :ref:`pages/prompts/rawlist:Choices` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default value of the prompt.
            This will be used to determine which choice is highlighted (current selection),
            The default value should be the value of one of the choices.
            For :class:`.RawlistPrompt` specifically, default value can also be value between 0-9.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        separator: Separator symbol. Custom symbol that will be used as a separator between the choice index number and the choices.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        pointer: Pointer symbol. Customer symbol that will be used to indicate the current choice selection.
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
        multiselect: Enable multi-selection on choices.
            You can use `validate` parameter to control min/max selections.
            Setting to True will also change the result from a single value to a list of values.
        marker: Marker Symbol. Custom symbol to indicate if a choice is selected.
            This will take effects when `multiselect` is True.
        marker_pl: Marker place holder when the choice is not selected.
            This is empty space by default.
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
        >>> result = inquirer.rawlist(message="Select one:", choices=[1, 2, 3]).execute()
        >>> print(result)
        1
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        choices: InquirerPyListChoices,
        default: InquirerPyDefault = None,
        separator: str = ") ",
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = " ",
        instruction: str = "",
        long_instruction: str = "",
        transformer: Optional[Callable[[Any], Any]] = None,
        filter: Optional[Callable[[Any], Any]] = None,
        height: Optional[Union[int, str]] = None,
        max_height: Optional[Union[int, str]] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        marker_pl: str = " ",
        border: bool = False,
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
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
        )

    def _on_rendered(self, _) -> None:
        """Override this method to apply custom keybindings.

        Needs to creat these kb in the callback due to `after_render`
        retrieve the choices asynchronously.

        Check if fetched choices exceed the limit of 9, raise
        InvalidArgument exception.
        """

        def keybinding_factory(choice):
            @self.register_kb(str(choice["display_index"]))
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
