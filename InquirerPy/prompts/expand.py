"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Dict, List, Literal, Tuple, Union

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


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
    """

    def __init__(
        self,
        options: List[Dict[str, Any]],
        default: str = None,
        pointer: str = " ",
        separator: str = ")",
    ) -> None:
        """Construct UIControl object and initialise options."""
        self.pointer = "%s " % pointer
        self.separator = separator
        self.expanded = False
        self.key_maps = {"h": -1}
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
                ("", self.options[self.selected_option_index]["value"])
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
        default: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        symbol: str = "?",
        pointer: str = " ",
        separator: str = ")",
    ) -> None:
        """Create the application and apply keybindings."""
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            options, default, pointer, separator
        )
        super().__init__(message, style, editing_mode, symbol)

        def keybinding_factory(key):
            @self.kb.add(key)
            def keybinding(_) -> None:
                self.content_control.selected_option_index = (
                    self.content_control.key_maps[key]
                )
