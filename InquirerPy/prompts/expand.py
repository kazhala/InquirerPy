"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Dict, List, Literal, NamedTuple, Tuple

from InquirerPy.base import (
    BaseComplexPrompt,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


class ExpandHelp(NamedTuple):
    """A struct class to identify if user selected the help option."""

    help_msg: str


class InquirerPyExpandControl(InquirerPyUIControl):
    """A content control intended to be used by `prompt_toolkit` window.

    All parameter types and purposes, reference `ExpandPrompt`.
    """

    def __init__(
        self,
        options: List[Dict[str, Any]],
        default: str,
        pointer: str,
        separator: str,
        help_msg: str,
        expand_pointer: str,
    ) -> None:
        """Construct content control object and initialise options."""
        self.pointer = "%s " % pointer
        self.separator = separator
        self.expanded = False
        self.key_maps = {}
        self.expand_pointer = expand_pointer
        super().__init__(options, default)

        try:
            count = 0
            separator_count = 0
            for raw_option, option in zip(options, self.options):
                if not isinstance(raw_option, dict) and not isinstance(
                    raw_option, Separator
                ):
                    raise InvalidArgument(
                        "expand type prompt require each option to be a dictionary."
                    )
                if isinstance(raw_option, Separator):
                    separator_count += 1
                else:
                    option["key"] = raw_option["key"]
                    self.key_maps[option["key"]] = count
                count += 1
        except KeyError:
            raise RequiredKeyNotFound(
                "each option require the dictionary key 'key' to be present."
            )

        self.options.append(
            {"key": "h", "value": ExpandHelp(help_msg), "name": help_msg}
        )
        self.key_maps["h"] = len(self.options) - 1

        if self.selected_option_index == 0:
            for index, option in enumerate(self.options):
                if isinstance(option["value"], Separator):
                    continue
                if option["key"] == default:
                    self.selected_option_index = index
                    break

    def _get_formatted_options(self) -> List[Tuple[str, str]]:
        """Override this parent class method as expand require visual switch of content.

        1. non expand mode
        2. expand mode
        """
        if self.expanded:
            return super()._get_formatted_options()
        else:
            display_choices = []
            display_choices.append(("class:pointer", "%s " % self.expand_pointer))
            display_choices.append(
                ("", self.options[self.selected_option_index]["name"])
            )
        return display_choices

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", self.pointer))
        if not isinstance(option["value"], Separator):
            display_message.append(
                ("class:pointer", "%s%s " % (option["key"], self.separator))
            )
        display_message.append(("class:pointer", option["name"]))
        return display_message

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", len(self.pointer) * " "))
        if not isinstance(option["value"], Separator):
            display_message.append(("", "%s%s " % (option["key"], self.separator)))
        display_message.append(("", option["name"]))
        return display_message


class ExpandPrompt(BaseComplexPrompt):
    """Create a `prompt_toolkit` application and responsible to render the expand prompt.

    Prompt contains 2 state, expanded and not expanded. The visual effect are
    all controled via InquirerPyExpandControl under one window.

    :param message: message to ask user
    :type message: str
    :param options: list of options to display
    :type options: List[Dict[str, Any]]
    :param default: default value, needs to be a key of the options
    :type default: str
    :param style: style dict to apply to the prompt
    :type style: Dict[str, str]
    :param editing_mode: controls the keybindings of movement
    :type editing_mode: Literal["default", "emacs", "vim"]
    :param symbol: question symbol to display
    :type symbol: str
    :param pointer: pointer symbol to indicate current selected line
    :type pointer: str
    :param separator: separator symbol to display between the shortcut key and the content
    :type separator: str
    :param help_msg: help message to display to the user
    :type help_msg: str
    :param expand_pointer: visual pointer before expansion of the prompt
    :type expand_pointer: str
    """

    def __init__(
        self,
        message: str,
        options: List[Dict[str, Any]],
        default: str = "",
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        symbol: str = "?",
        pointer: str = " ",
        separator: str = ")",
        help_msg: str = "Help, list all options",
        expand_pointer: str = INQUIRERPY_POINTER_SEQUENCE,
    ) -> None:
        """Create the application and apply keybindings."""
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            options, default, pointer, separator, help_msg, expand_pointer
        )
        super().__init__(message, style, editing_mode, symbol)

        def keybinding_factory(key):
            @self.kb.add(key.lower())
            def keybinding(_) -> None:
                if key == "h":
                    self.content_control.expanded = not self.content_control.expanded
                else:
                    self.content_control.selected_option_index = (
                        self.content_control.key_maps[key]
                    )

            return keybinding

        for option in self.content_control.options:
            if not isinstance(option["value"], Separator):
                keybinding_factory(option["key"])

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up.

        Overriding this method to skip the help option.
        """
        while True:
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index - 1
            ) % self.content_control.option_count
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down.

        Overriding this method to skip the help option.
        """
        while True:
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index + 1
            ) % self.content_control.option_count
            if not isinstance(
                self.content_control.selection["value"], Separator
            ) and not isinstance(self.content_control.selection["value"], ExpandHelp):
                break

    @property
    def instruction(self) -> str:
        """Construct the instruction behind the question.

        :return: instruction
        :rtype: str
        """
        return "(%s)" % "".join(self.content_control.key_maps.keys())

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Overriding this method to allow multiple formatted class to be displayed.
        """
        display_message = []
        display_message.append(("class:symbol", self.symbol))
        display_message.append(("class:question", " %s" % self.message))
        if self.status["answered"]:
            display_message.append(("class:answer", " %s" % self.status["result"]))
        else:
            display_message.append(("class:instruction", " %s" % self.instruction))
            display_message.append(
                ("class:input", " %s" % self.content_control.selection["key"])
            )
        return display_message
