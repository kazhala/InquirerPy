"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseComplexPrompt, BaseListPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["ExpandPrompt"]


class ExpandHelp(NamedTuple):
    """A struct class to identify if user selected the help choice."""

    help_msg: str


class InquirerPyExpandControl(InquirerPyUIControl):
    """A content control intended to be used by `prompt_toolkit` window.

    All parameter types and purposes, reference `ExpandPrompt`.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
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
        """Construct content control object and initialise choices."""
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
                        "expand type prompt require each choice to be a dictionary or Separator."
                    )
                if isinstance(raw_choice, Separator):
                    separator_count += 1
                else:
                    choice["key"] = raw_choice["key"]
                    self._key_maps[choice["key"]] = count
                count += 1
        except KeyError:
            raise RequiredKeyNotFound(
                "each dictionary choice require the dictionary key 'key' to be present."
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

        1. non expand mode
        2. expand mode
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


class ExpandPrompt(BaseListPrompt):
    """Create a `prompt_toolkit` application and responsible to render the expand prompt.

    Prompt contains 2 state, expanded and not expanded. The visual effect are
    all controled via InquirerPyExpandControl under one window.

    :param message: Message to ask user.
    :param choices: List of choices to display.
    :param default: Default value, can be a key of the choices or a value.
    :param style: Style dict to apply to the prompt.
    :param vi_mode: Use vi keybindings for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: THe custom symbol to display infront of the question after its answered.
    :param pointer: Pointer symbol to indicate current selected line.
    :param separator: Separator symbol to display between the shortcut key and the content.
    :param help_msg: Help message to display to the user.
    :param expand_pointer: Visual pointer before expansion of the prompt.
    :param instruction: Override the default instruction e.g. (Yabh).
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param height: Preferred height of the choice window.
    :param max_height: Max height choice window should reach.
    :param multiselect: Enable multiselectiion.
    :param marker: Marker symbol to indicate selected choice in multiselect mode
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
        session_result: SessionResult = None,
    ) -> None:
        """Create the application and apply keybindings."""
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

    def _after_render(self, application) -> None:
        """Override this method to apply custom keybindings.

        Since `self.content_control.choices` may not exists before
        `Application` is created if its a callable, create these
        chocies based keybindings in the after_render call.
        """
        if not self._rendered:
            super()._after_render(application)

            def keybinding_factory(key):
                @self._register_kb(key.lower())
                def keybinding(_) -> None:
                    if key == "h":
                        self.content_control._expanded = (
                            not self.content_control._expanded
                        )
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
            cap = BaseComplexPrompt._handle_up(self)
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
            cap = BaseComplexPrompt._handle_down(self)
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
