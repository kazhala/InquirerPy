"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Dict, List, Literal, NamedTuple, Tuple

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


class ExpandHelp(NamedTuple):
    """A struct class to identify if user selected the help option."""

    help_msg: str


class InquirerPyExpandControl(InquirerPyUIControl):
    """A UI control object intended to be used by `prompt_toolkit` window.

    :param options: list of options to display
    :type options: List[Dict[str, Any]]
    :param default: default value, must be one of the "key" of the options
    :type default: str
    :param pointer: the pointer symbol to use indicating current highlighted line
    :type pointer: str
    :param separator: separator symbol to display between the shortcut key and the content
    :type separator: str
    :param help_msg: help message to display to the user
    :type help_msg: str
    """

    def __init__(
        self,
        options: List[Dict[str, Any]],
        default: str = None,
        pointer: str = " ",
        separator: str = ")",
        help_msg: str = "Help, list all options",
    ) -> None:
        """Construct UIControl object and initialise options."""
        self.pointer = "%s " % pointer
        self.separator = separator
        self.expanded = False
        self.key_maps = {}
        super().__init__(options, default)

        try:
            count = 0
            separator_count = 0
            for raw_option, option in zip(options, self.options):
                if not isinstance(raw_option, dict):
                    raise InvalidArgument(
                        "expand type prompt require each option to be a dictionary."
                    )
                if isinstance(option["value"], Separator):
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

    def _get_formatted_options(self) -> List[Tuple[str, str]]:
        """Override this parent class method as expand require visual switch of content.

        1. non expand mode
        2. expand mode

        :return: a list of formatted options
        :rtype: List[Tuple[str, str]]
        """
        if self.expanded:
            return super()._get_formatted_options()
        else:
            display_choices = []
            display_choices.append(("class:pointer", ">> "))
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

    def _set_selected_option(self, key: str) -> None:
        self.selected_option_index = self.key_maps[key]


class ExpandPrompt(BaseComplexPrompt):
    """Create a `prompt_toolkit` application and responsible to render the expand prompt.

    :param options: list of options to display
    :type options: List[Dict[str, Any]]
    """

    def __init__(
        self,
        message: str,
        options: List[Dict[str, Any]],
        default: str = None,
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        symbol: str = "?",
        pointer: str = " ",
        separator: str = ")",
        help_msg: str = "Help, list all options",
    ) -> None:
        """Create the application and apply keybindings."""
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            options, default, pointer, separator, help_msg
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

    def handle_up(self) -> None:
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

    def handle_down(self) -> None:
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
        """Render the instruction behind the question.

        This method is also responsible to display the user input.
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