"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Dict, List, Tuple, Union

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
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
        options: List[Union[Any, Dict[str, Any]]],
        default: str = None,
        pointer: str = " ",
        separator: str = ")",
    ) -> None:
        """Construct UIControl object and initialise options."""
        self.pointer = "%s " % pointer
        self.separator = separator
        super().__init__(options, default)

        for raw_option, option in zip(options, self.options):
            option["key"] = raw_option["key"]

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
