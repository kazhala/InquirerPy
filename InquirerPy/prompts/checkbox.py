"""Module contains checkbox prompt."""

from typing import Any, Dict, List, Tuple, Union

from InquirerPy.base import (
    BaseComplexPrompt,
    INQUIRERPY_EMPTY_HEX_SEQUENCE,
    INQUIRERPY_FILL_HEX_SEQUENCE,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)


class InquirerPyCheckboxControl(InquirerPyUIControl):
    """A UIControl class intended to be used by `prompt_toolkit` window.

    Used to dynamically update the content and indicate the current user selection

    :param options: a list of options to display
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default value for selection
    :type default: Any
    :param pointer: the pointer to display, indicating current line, default is unicode ">"
    :type pointer: str
    :param selected_symbol: the symbol to indicate selected options
    :type selected_symbol: str
    :param not_selected_symbol: the symbol to indicate not selected options
    :type not_selected_symbol: str
    """

    def __init__(
        self,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        selected_symbol: str = INQUIRERPY_FILL_HEX_SEQUENCE,
        not_selected_symbol: str = INQUIRERPY_EMPTY_HEX_SEQUENCE,
    ) -> None:
        """Initialise required attributes and call base class."""
        self.pointer = pointer
        self.selected_symbol = selected_symbol
        self.not_selected_symbol = not_selected_symbol
        self.selected_options = set()
        super().__init__(options, default)

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", " %s " % self.pointer))
        display_message.append(
            ("class:selected", self.selected_symbol)
            if option["name"] in self.selected_options
            else ("", self.not_selected_symbol)
        )
        display_message.append(("class:pointer", str(option["name"])))
        return display_message

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", "   "))
        display_message.append(
            ("class:selected", self.selected_symbol)
            if option["name"] in self.selected_options
            else ("", self.not_selected_symbol)
        )
        display_message.append(("", option["name"]))
        return display_message
