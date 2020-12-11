"""Module contains checkbox prompt."""

from typing import Any, Dict, List, Literal, Tuple, Union

from prompt_toolkit.keys import Keys

from InquirerPy.base import (
    BaseComplexPrompt,
    INQUIRERPY_EMPTY_HEX_SEQUENCE,
    INQUIRERPY_FILL_HEX_SEQUENCE,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)
from InquirerPy.separator import Separator


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
    :param disabled_symbol: the symbol to indicate not selected options
    :type disabled_symbol: str
    """

    def __init__(
        self,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = INQUIRERPY_EMPTY_HEX_SEQUENCE,
    ) -> None:
        """Initialise required attributes and call base class."""
        self.pointer = "%s " % pointer
        self.enabled_symbol = enabled_symbol
        self.disabled_symbol = disabled_symbol
        super().__init__(options, default)

        for raw_option, option in zip(options, self.options):
            if isinstance(raw_option, dict):
                option["enabled"] = raw_option.get("enabled", False)
            else:
                option["enabled"] = False

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", self.pointer))
        if not isinstance(option["value"], Separator):
            display_message.append(
                (
                    "class:checkbox",
                    "%s " % self.enabled_symbol
                    if option["enabled"]
                    else "%s " % self.disabled_symbol,
                )
            )
        display_message.append(("class:pointer", option["name"]))
        return display_message

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", len(self.pointer) * " "))
        if not isinstance(option["value"], Separator):
            display_message.append(
                (
                    "class:checkbox",
                    "%s " % self.enabled_symbol
                    if option["enabled"]
                    else "%s " % self.disabled_symbol,
                )
            )
        display_message.append(("", option["name"]))
        return display_message


class CheckboxPrompt(BaseComplexPrompt):
    """A wrapper class around `prompt_toolkit` Application to create a checkbox prompt.

    :param message: message to display
    :type message: str
    :param options: list of options to display
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param style: a dictionary of style
    :type style: Dict[str, str]
    :param editing_mode: editing_mode of the prompt
    :type editing_mode: Literal["emacs", "default", "vim"]
    :param symbol: question symbol to display
    :type symbol: str
    :param pointer: the pointer symbol to display
    :type pointer: str
    :param enabled_symbol: symbol indicating enabled box
    :type enabled_symbol: str
    :param disabled_symbol: symbol indicating not selected symbol
    :type disabled_symbol: str
    :param instruction: instruction to display after the message
    :type instruction: str
    """

    def __init__(
        self,
        message: str,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        symbol: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        enabled_symbol: str = INQUIRERPY_FILL_HEX_SEQUENCE,
        disabled_symbol: str = INQUIRERPY_EMPTY_HEX_SEQUENCE,
        instruction: str = "",
    ) -> None:
        """Initialise the content_control and create Application."""
        self.content_control = InquirerPyCheckboxControl(
            options, default, pointer, enabled_symbol, disabled_symbol
        )
        super().__init__(message, style, editing_mode, symbol, instruction)

        @self.kb.add(" ")
        def _(event) -> None:
            self._toggle_option()

        @self.kb.add(Keys.Tab)
        def _(event) -> None:
            self._toggle_option()
            self._handle_down()

        @self.kb.add(Keys.BackTab)
        def _(event) -> None:
            self._toggle_option()
            self._handle_up()

        @self.kb.add("a")
        def _(event) -> None:
            self._toggle_all(True)

        @self.kb.add("i")
        def _(event) -> None:
            self._toggle_all()

    def _toggle_option(self) -> None:
        self.content_control.selection["enabled"] = not self.content_control.selection[
            "enabled"
        ]

    def _toggle_all(self, value: bool = None) -> None:
        for option in self.content_control.options:
            if isinstance(option["value"], Separator):
                continue
            option["enabled"] = value if value else not option["enabled"]

    def handle_enter(self, event) -> None:
        """Handle the event when user hit enter.

        Get all current user selected options and exit application using them as the result.
        """
        self.status["answered"] = True
        self.status["result"] = [option["name"] for option in self.selected_options]
        event.app.exit(result=[option["value"] for option in self.selected_options])

    @property
    def selected_options(self) -> List[Any]:
        """Get all user selected options."""

        def filter_option(option):
            return not isinstance(option, Separator) and option["enabled"]

        return list(filter(filter_option, self.content_control.options))
