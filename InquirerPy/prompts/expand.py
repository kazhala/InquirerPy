"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.base import BaseListPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult


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
    ) -> None:
        """Construct content control object and initialise choices."""
        self._pointer = pointer
        self._separator = separator
        self._expanded = False
        self._key_maps = {}
        self._expand_pointer = "%s " % expand_pointer
        self._marker = marker
        self._help_msg = help_msg
        super().__init__(
            choices=choices, default=default, session_result=session_result
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
                self._marker if choice["enabled"] else " ",
            )
        )
        if not isinstance(choice["value"], Separator):
            display_choices.append(
                ("class:pointer", "%s%s " % (choice["key"], self._separator))
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
                self._marker if choice["enabled"] else " ",
            )
        )
        if not isinstance(choice["value"], Separator):
            display_choices.append(("", "%s%s " % (choice["key"], self._separator)))
            display_choices.append(("", choice["name"]))
        else:
            display_choices.append(("class:separator", choice["name"]))
        return display_choices


class ExpandPrompt(BaseListPrompt):
    """Create a `prompt_toolkit` application and responsible to render the expand prompt.

    Prompt contains 2 state, expanded and not expanded. The visual effect are
    all controled via InquirerPyExpandControl under one window.

    :param message: message to ask user
    :type message: Union[str, Callable[[SessionResult], str]]
    :param choices: list of choices to display
    :type choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
    :param default: default value, can be a key of the choices or a value
    :type default: Any
    :param style: style dict to apply to the prompt
    :type style: InquirerPyStyle
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: bool
    :param qmark: question qmark to display
    :type qmark: str
    :param pointer: pointer qmark to indicate current selected line
    :type pointer: str
    :param separator: separator qmark to display between the shortcut key and the content
    :type separator: str
    :param help_msg: help message to display to the user
    :type help_msg: str
    :param expand_pointer: visual pointer before expansion of the prompt
    :type expand_pointer: str
    :param instruction: override the default instruction e.g. (Yabh)
    :type instruction: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[Any], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
    :param multiselect: enable multiselectiion
    :type multiselect: bool
    :param marker: marker symbol to indicate selected choice in multiselect mode
    :type marker: str
    :param validate: a callable or Validator instance to validate user selection
    :type validate: Union[Callable[[Any], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param keybindings: custom keybindings to apply
    :type keybindings: Dict[str, List[Dict[str, Any]]]
    :param show_cursor: display cursor at the end of the prompt
    :type show_cursor: bool
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = "",
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        pointer: str = " ",
        separator: str = ")",
        help_msg: str = "Help, list all choices",
        expand_pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        multiselect: bool = False,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        show_cursor: bool = True,
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
            session_result=session_result,
        )
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
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
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index - 1
            ) % self.content_control.choice_count
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down.

        Overriding this method to skip the help choice.
        """
        if not self.content_control._expanded:
            return
        while True:
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index + 1
            ) % self.content_control.choice_count
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break

    @property
    def instruction(self) -> str:
        """Construct the instruction behind the question.

        If _instruction exists, use that.

        :return: instruction
        :rtype: str
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
                ("class:input", " %s" % self.content_control.selection["key"])
            )
        return display_message

    def _toggle_all(self, value: bool = None) -> None:
        """Override this method to ignore `ExpandHelp`.

        :param value: sepcify a value to toggle
        :type value: bool
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
