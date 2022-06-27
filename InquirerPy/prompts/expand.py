"""Module contains the class to create an expand prompt."""
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple, Union

from InquirerPy.base import BaseListPrompt, InquirerPyUIListControl
from InquirerPy.base.control import Choice
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
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

__all__ = ["ExpandPrompt", "ExpandHelp", "ExpandChoice"]


@dataclass
class ExpandHelp:
    """Help choice for the :class:`.ExpandPrompt`.

    Args:
        key: The key to bind to toggle the expansion of the prompt.
        message: The help message.
    """

    key: str = "h"
    message: str = "Help, list all choices"


@dataclass
class ExpandChoice(Choice):
    """Choice class for :class:`.ExpandPrompt`.

    See Also:
        :class:`~InquirerPy.base.control.Choice`

    Args:
        value: The value of the choice when user selects this choice.
        name: The value that should be presented to the user prior/after selection of the choice.
            This value is optional, if not provided, it will fallback to the string representation of `value`.
        enabled: Indicates if the choice should be pre-selected.
            This only has effects when the prompt has `multiselect` enabled.
        key: Char to bind to the choice. Pressing this value will jump to the choice,
            If this value is missing, the first char of the `str(value)` will be used as the key.
    """

    key: Optional[str] = None

    def __post_init__(self):
        """Assign stringify value to name and also create key using the first char of the value if not present."""
        super().__post_init__()
        if self.key is None:
            self.key = str(self.value)[0].lower()


class InquirerPyExpandControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.ExpandPrompt`.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        default: Any,
        pointer: str,
        separator: str,
        expand_help: ExpandHelp,
        expand_pointer: str,
        marker: str,
        session_result: Optional[InquirerPySessionResult],
        multiselect: bool,
        marker_pl: str,
    ) -> None:
        self._pointer = pointer
        self._separator = separator
        self._expanded = False
        self._expand_pointer = expand_pointer
        self._marker = marker
        self._marker_pl = marker_pl
        self._expand_help = expand_help
        super().__init__(
            choices=choices,
            default=default,
            session_result=session_result,
            multiselect=multiselect,
        )

    def _format_choices(self) -> None:
        self._key_maps = {}
        try:
            count = 0
            separator_count = 0
            for raw_choice, choice in zip(self._raw_choices, self.choices):  # type: ignore
                if (
                    not isinstance(raw_choice, dict)
                    and not isinstance(raw_choice, Separator)
                    and not isinstance(raw_choice, ExpandChoice)
                ):
                    raise InvalidArgument(
                        "expand prompt argument choices requires each choice to be type of dictionary or Separator or ExpandChoice"
                    )
                if isinstance(raw_choice, Separator):
                    separator_count += 1
                else:
                    choice["key"] = (
                        raw_choice.key
                        if isinstance(raw_choice, ExpandChoice)
                        else raw_choice["key"]
                    )
                    self._key_maps[choice["key"]] = count
                count += 1
        except KeyError:
            raise RequiredKeyNotFound(
                "expand prompt choice requires a key 'key' to exists"
            )

        self.choices.append(
            {
                "key": self._expand_help.key,
                "value": self._expand_help,
                "name": self._expand_help.message,
                "enabled": False,
            }
        )
        self._key_maps[self._expand_help.key] = len(self.choices) - 1

        first_valid_choice_index = 0
        while isinstance(self.choices[first_valid_choice_index]["value"], Separator):
            first_valid_choice_index += 1
        if self.selected_choice_index == first_valid_choice_index:
            for index, choice in enumerate(self.choices):
                if isinstance(choice["value"], Separator):
                    continue
                if choice["key"] == self._default:
                    self.selected_choice_index = index
                    break

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Override this parent class method as expand require visual switch of content.

        Two types of mode:
            * non expand mode
            * expand mode
        """
        if self._expanded:
            return super()._get_formatted_choices()
        else:
            display_choices = []
            display_choices.append(("class:pointer", self._expand_pointer))
            display_choices.append(
                ("", self.choices[self.selected_choice_index]["name"])
            )
        return display_choices

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
                ("class:pointer", "%s%s" % (choice["key"], self._separator))
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
            display_choices.append(("", "%s%s" % (choice["key"], self._separator)))
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class ExpandPrompt(ListPrompt):
    """Create a compact prompt with the ability to expand.

    A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Contains a list of chocies binded to a shortcut letter.
    The prompt can be expanded using `h` key.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        choices: List of choices to display and select.
            Refer to :ref:`pages/prompts/expand:Choices` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default value of the prompt.
            This will be used to determine which choice is highlighted (current selection),
            The default value should the value of one of the choices.
            For :class:`.ExpandPrompt` specifically, default value can also be a `choice["key"]` which is the shortcut key for the choice.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        separator: Separator symbol. Custom symbol that will be used as a separator between the choice index number and the choices.
        help_msg: This parameter is DEPRECATED. Use expand_help instead.
        expand_help: The help configuration for the prompt. Must be an instance of :class:`.ExpandHelp`.
            If this value is None, the default help key will be binded to `h` and the default help message would be
            "Help, List all choices."
        expand_pointer: Pointer symbol before prompt expansion. Custom symbol that will be displayed to indicate the prompt is not expanded.
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
        >>> result = inquirer.expand(message="Select one:", choices[{"name": "1", "value": "1", "key": "a"}]).execute()
        >>> print(result)
        "1"
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        choices: InquirerPyListChoices,
        default: InquirerPyDefault = "",
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = " ",
        separator: str = ") ",
        help_msg: str = "Help, list all choices",
        expand_help: Optional[ExpandHelp] = None,
        expand_pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
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
        if expand_help is None:
            expand_help = ExpandHelp(message=help_msg)
        self._expand_help = expand_help
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            choices=choices,
            default=default,
            pointer=pointer,
            separator=separator,
            expand_help=expand_help,
            expand_pointer=expand_pointer,
            marker=marker,
            marker_pl=marker_pl,
            session_result=session_result,
            multiselect=multiselect,
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
            multiselect=multiselect,
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
        """

        def keybinding_factory(key):
            @self.register_kb(key.lower())
            def keybinding(_) -> None:
                if key == self._expand_help.key:
                    self.content_control._expanded = not self.content_control._expanded
                else:
                    self.content_control.selected_choice_index = (
                        self.content_control._key_maps[key]
                    )

            return keybinding

        for choice in self.content_control.choices:
            if not isinstance(choice["value"], Separator):
                keybinding_factory(choice["key"])

    def _handle_up(self, event) -> None:
        """Handle the event when user attempt to move up.

        Overriding this method to skip the help choice.
        """
        if not self.content_control._expanded:
            return
        while True:
            cap = BaseListPrompt._handle_up(self, event)
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break
            else:
                if cap and not self._cycle:
                    self._handle_down(event)
                    break

    def _handle_down(self, event) -> None:
        """Handle the event when user attempt to move down.

        Overriding this method to skip the help choice.
        """
        if not self.content_control._expanded:
            return
        while True:
            cap = BaseListPrompt._handle_down(self, event)
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break
            elif (
                isinstance(self.content_control.selection["value"], ExpandHelp)
                and not self._cycle
            ):
                self._handle_up(event)
                break
            else:
                if cap and not self._cycle:
                    self._handle_up(event)
                    break

    @property
    def instruction(self) -> str:
        """Construct the instruction behind the question.

        If _instruction exists, use that.

        :return: The instruction text.
        """
        return (
            "(%s)" % "".join(self.content_control._key_maps.keys())
            if not self._instruction
            else self._instruction
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Overriding this method to allow multiple formatted class to be displayed.
        """
        display_message = super()._get_prompt_message()
        if not self.status["answered"]:
            display_message.append(
                ("class:input", self.content_control.selection["key"])
            )
        return display_message

    def _handle_toggle_all(self, _, value: Optional[bool] = None) -> None:
        """Override this method to ignore `ExpandHelp`.

        :param value: Specify a value to toggle.
        """
        if not self.content_control._expanded:
            return
        for choice in self.content_control.choices:
            if isinstance(choice["value"], Separator) or isinstance(
                choice["value"], ExpandHelp
            ):
                continue
            choice["enabled"] = value if value else not choice["enabled"]

    def _handle_toggle_choice(self, event) -> None:
        """Override this method to ignore keypress when not expanded."""
        if not self.content_control._expanded:
            return
        super()._handle_toggle_choice(event)
