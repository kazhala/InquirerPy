"""Module contains the rawlist prompt."""
from typing import Any, Dict, List, Literal, Tuple, Union

from InquirerPy.base import (
    BaseComplexPrompt,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)
from InquirerPy.separator import Separator


class InquirerPyRawlistControl(InquirerPyUIControl):
    """A content control instance intended to used by `prompt_tool_kit` Window.

    Used to dynamically generate the content to display based on user interaction.

    :param options: available options
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: str
    :param pointer: the pointer symbol
    :type pointer: str
    :param separator: the separator between the index number and the options
        e.g. default separator is ")"
            1) whatever
            2) whatever
    :type separator: str
    """

    def __init__(
        self,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        separator: str = ")",
    ) -> None:
        """Construct the content control object and add the index to each option for visual purposes."""
        self.pointer = pointer
        self.separator = separator
        super().__init__(options, default)

        for index, option in enumerate(self.options):
            option["index"] = index + 1

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", " %s " % self.pointer))
        if not isinstance(option["value"], Separator):
            display_message.append(
                ("class:pointer", "%s%s " % (str(option["index"]), self.separator))
            )
        display_message.append(("class:pointer", option["name"]))
        return display_message

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", "   "))
        if not isinstance(option["value"], Separator):
            display_message.append(
                ("", "%s%s " % (str(option["index"]), self.separator))
            )
        display_message.append(("", option["name"]))
        return display_message


class RawlistPrompt(BaseComplexPrompt):
    """Used to create a rawlist prompt where user can use number to jump to items.

    :param message: message to display as question
    :type message: str
    :param options: list of options available for selection
    :type options: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param separator: the separator between the index number and the options
        e.g. default separator is ")"
            1) whatever
            2) whatever
    :type separator: str
    :param style: style for the prompt
    :type style: Dict[str, str]
    :param editing_mode: keybinding mode
    :type editing_mode: Literal["emacs", "vim", "default"]
    :param symbol: question symbol to display
    :type symbol: str
    :param pointer: pointer symbol to display
    :type pointer: str
    :param instruction: instruction to display at the end of the prompt
    :type instruction: str
    """

    def __init__(
        self,
        message: str,
        options: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        separator: str = ")",
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "vim", "default"] = "default",
        symbol: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
    ) -> None:
        """Construct content control and initialise the application while also apply keybindings."""
        self.content_control = InquirerPyRawlistControl(
            options, default, pointer, separator
        )
        self._instruction = instruction
        super().__init__(message, style, editing_mode, symbol)

        def keybinding_factory(index):
            @self.kb.add(index)
            def keybinding(_) -> None:
                self.content_control.selected_option_index = int(index)
                self.handle_up()

            return keybinding

        for option in self.content_control.options:
            keybinding_factory(str(option["index"]))

    def handle_enter(self, event) -> None:
        """Handle the event of user hitting enter."""
        self.status["answered"] = True
        self.status["result"] = self.content_control.selection["name"]
        event.app.exit(result=self.content_control.selection["value"])

    @property
    def instruction(self) -> str:
        """Get the instruction to display."""
        return self._instruction
