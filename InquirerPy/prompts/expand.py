"""Module contains the class to create an expand prompt."""
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseListPrompt, InquirerPyUIListControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, ListChoices, SessionResult

__all__ = ["ExpandPrompt"]


class ExpandHelp(NamedTuple):
    """A :class:`typing.NamedTuple` to use as the help choice."""

    help_msg: str


class InquirerPyExpandControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    Reference the parameter definition in :class:`.ExpandPrompt`.
    """

    def __init__(
        self,
        choices: ListChoices,
        default: Any,
        pointer: str,
        separator: str,
        help_msg: str,
        expand_pointer: str,
        marker: str,
        session_result: Optional[SessionResult],
        multiselect: bool,
        marker_pl: str = " ",
    ) -> None:
        self._pointer = pointer
        self._separator = separator
        self._expanded = False
        self._key_maps = {}
        self._expand_pointer = expand_pointer
        self._marker = marker
        self._marker_pl = marker_pl
        self._help_msg = help_msg
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
                if not isinstance(raw_choice, dict) and not isinstance(
                    raw_choice, Separator
                ):
                    raise InvalidArgument(
                        "expand prompt argument choices requires each choice to be type of dictionary or Separator"
                    )
                if isinstance(raw_choice, Separator):
                    separator_count += 1
                else:
                    choice["key"] = raw_choice["key"]
                    self._key_maps[choice["key"]] = count
                count += 1
        except KeyError:
            raise RequiredKeyNotFound(
                "expand prompt choice requires a key 'key' to exists"
            )

        self.choices.append(
            {
                "key": "h",
                "value": ExpandHelp(self._help_msg),
                "name": self._help_msg,
                "enabled": False,
            }
        )
        self._key_maps["h"] = len(self.choices) - 1

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
    """A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Create a compact prompt with a list of chocies identified with a single letter.
    The prompt can be expanded using `h` key.

    Args:
        message: The question to ask the user.
        choices (ListChoices): List of choices to display.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        vi_mode: Use vim keybinding for the prompt.
        default: The default value. This will affect where the cursor starts from. Should be one of the choice value.
        separator: The separator between the choice letter and the choices.
        help_msg: The help message to display.
        expand_pointer: Pointer to display before the prompt is expanded.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        pointer: Custom symbol that will be used to indicate the current choice selection.
        instruction: Short instruction to display next to the `message`.
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
        >>> result = ExpandPrompt(message="Select one:", choices=[{"name": "1", "value": "1", "key": "a"}]).execute()
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: ListChoices,
        default: Any = "",
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        pointer: str = " ",
        separator: str = ") ",
        help_msg: str = "Help, list all choices",
        expand_pointer: str = "%s " % INQUIRERPY_POINTER_SEQUENCE,
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
        set_exception_handler: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            choices=choices,
            default=default,
            pointer=pointer,
            separator=separator,
            help_msg=help_msg,
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
        """
        self._redraw()

        def keybinding_factory(key):
            @self._register_kb(key.lower())
            def keybinding(_) -> None:
                if key == "h":
                    self.content_control._expanded = not self.content_control._expanded
                else:
                    self.content_control.selected_choice_index = (
                        self.content_control._key_maps[key]
                    )

            return keybinding

        for choice in self.content_control.choices:
            if not isinstance(choice["value"], Separator):
                keybinding_factory(choice["key"])

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up.

        Overriding this method to skip the help choice.
        """
        if not self.content_control._expanded:
            return
        while True:
            cap = BaseListPrompt._handle_up(self)
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break
            else:
                if cap and not self._cycle:
                    self._handle_down()
                    break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down.

        Overriding this method to skip the help choice.
        """
        if not self.content_control._expanded:
            return
        while True:
            cap = BaseListPrompt._handle_down(self)
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break
            elif (
                isinstance(self.content_control.selection["value"], ExpandHelp)
                and not self._cycle
            ):
                self._handle_up()
                break
            else:
                if cap and not self._cycle:
                    self._handle_up()
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

    def _toggle_all(self, value: bool = None) -> None:
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

    def _toggle_choice(self) -> None:
        """Override this method to ignore keypress when not expanded."""
        if not self.content_control._expanded:
            return
        super()._toggle_choice()
