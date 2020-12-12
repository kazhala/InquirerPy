"""Module contains the rawlist prompt."""
from typing import Any, Dict, List, Literal, Tuple, Union

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.separator import Separator


class InquirerPyRawlistControl(InquirerPyUIControl):
    """A content control instance intended to used by `prompt_tool_kit` Window.

    All parameter types and purposes, reference `RawlistPrompt`.
    """

    def __init__(
        self,
        choices: List[Union[Any, Dict[str, Any]]],
        default: Any,
        pointer: str,
        separator: str,
    ) -> None:
        """Construct the content control object and add the index to each choice for visual purposes."""
        self.pointer = "%s " % pointer
        self.separator = separator
        super().__init__(choices, default)

        separator_count = 0
        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                separator_count += 1
                continue
            choice["display_index"] = index + 1 - separator_count
            choice["actual_index"] = index

        first_valid_choice_index = 0
        while isinstance(self.choices[first_valid_choice_index]["value"], Separator):
            first_valid_choice_index += 1
        if self.selected_choice_index == first_valid_choice_index:
            for choice in self.choices:
                if isinstance(choice["value"], Separator):
                    continue
                if choice["display_index"] == default:
                    self.selected_choice_index = choice["actual_index"]
                    break

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", self.pointer))
        if not isinstance(choice["value"], Separator):
            display_message.append(
                (
                    "class:pointer",
                    "%s%s " % (str(choice["display_index"]), self.separator),
                )
            )
        display_message.append(("class:pointer", choice["name"]))
        return display_message

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", len(self.pointer) * " "))
        if not isinstance(choice["value"], Separator):
            display_message.append(
                ("", "%s%s " % (str(choice["display_index"]), self.separator))
            )
        display_message.append(("", choice["name"]))
        return display_message


class RawlistPrompt(BaseComplexPrompt):
    """Used to create a rawlist prompt where user can use number to jump to items.

    :param message: message to display as question
    :type message: str
    :param choices: list of choices available for selection
    :type choices: List[Union[Any, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param separator: the separator between the index number and the choices
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
        choices: List[Union[Any, Dict[str, Any]]],
        default: Any = None,
        separator: str = ")",
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "vim", "default"] = "default",
        symbol: str = "?",
        pointer: str = " ",
        instruction: str = "",
    ) -> None:
        """Construct content control and initialise the application while also apply keybindings."""
        self.content_control = InquirerPyRawlistControl(
            choices, default, pointer, separator
        )
        self._instruction = instruction
        super().__init__(message, style, editing_mode, symbol, instruction)

        def keybinding_factory(choice):
            @self.kb.add(str(choice["display_index"]))
            def keybinding(_) -> None:
                self.content_control.selected_choice_index = int(choice["actual_index"])

            return keybinding

        for choice in self.content_control.choices:
            if not isinstance(choice["value"], Separator):
                keybinding_factory(choice)
