"""Module contains the expand prompt and its related helper classes."""
from typing import Any, Callable, Dict, List, Literal, NamedTuple, Tuple, Union

from InquirerPy.base import BaseComplexPrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


class ExpandHelp(NamedTuple):
    """A struct class to identify if user selected the help choice."""

    help_msg: str


class InquirerPyExpandControl(InquirerPyUIControl):
    """A content control intended to be used by `prompt_toolkit` window.

    All parameter types and purposes, reference `ExpandPrompt`.
    """

    def __init__(
        self,
        choices: List[Union[Separator, Dict[str, Any]]],
        default: str,
        pointer: str,
        separator: str,
        help_msg: str,
        expand_pointer: str,
    ) -> None:
        """Construct content control object and initialise choices."""
        self.pointer = "%s " % pointer
        self.separator = separator
        self.expanded = False
        self.key_maps = {}
        self.expand_pointer = "%s " % expand_pointer
        super().__init__(choices, default)

        try:
            count = 0
            separator_count = 0
            for raw_choice, choice in zip(choices, self.choices):
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
                    self.key_maps[choice["key"]] = count
                count += 1
        except KeyError:
            raise RequiredKeyNotFound(
                "each dictionary choice require the dictionary key 'key' to be present."
            )

        self.choices.append(
            {"key": "h", "value": ExpandHelp(help_msg), "name": help_msg}
        )
        self.key_maps["h"] = len(self.choices) - 1

        first_valid_choice_index = 0
        while isinstance(self.choices[first_valid_choice_index]["value"], Separator):
            first_valid_choice_index += 1
        if self.selected_choice_index == first_valid_choice_index:
            for index, choice in enumerate(self.choices):
                if isinstance(choice["value"], Separator):
                    continue
                if choice["key"] == default:
                    self.selected_choice_index = index
                    break

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Override this parent class method as expand require visual switch of content.

        1. non expand mode
        2. expand mode
        """
        if self.expanded:
            return super()._get_formatted_choices()
        else:
            display_choices = []
            display_choices.append(("class:pointer", self.expand_pointer))
            display_choices.append(
                ("", self.choices[self.selected_choice_index]["name"])
            )
        return display_choices

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("class:pointer", self.pointer))
        if not isinstance(choice["value"], Separator):
            display_message.append(
                ("class:pointer", "%s%s " % (choice["key"], self.separator))
            )
        display_message.append(("class:pointer", choice["name"]))
        return display_message

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_message = []
        display_message.append(("", len(self.pointer) * " "))
        if not isinstance(choice["value"], Separator):
            display_message.append(("", "%s%s " % (choice["key"], self.separator)))
            display_message.append(("", choice["name"]))
        else:
            display_message.append(("class:separator", choice["name"]))
        return display_message


class ExpandPrompt(BaseComplexPrompt):
    """Create a `prompt_toolkit` application and responsible to render the expand prompt.

    Prompt contains 2 state, expanded and not expanded. The visual effect are
    all controled via InquirerPyExpandControl under one window.

    :param message: message to ask user
    :type message: str
    :param choices: list of choices to display
    :type choices: List[Union[Separator, Dict[str, Any]]]
    :param default: default value, needs to be a key of the choices
    :type default: str
    :param style: style dict to apply to the prompt
    :type style: Dict[str, str]
    :param editing_mode: controls the keybindings of movement
    :type editing_mode: Literal["default", "emacs", "vim"]
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
    :type transformer: Callable
    """

    def __init__(
        self,
        message: str,
        choices: List[Union[Dict[str, Any], Separator]],
        default: str = "",
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        qmark: str = "?",
        pointer: str = " ",
        separator: str = ")",
        help_msg: str = "Help, list all choices",
        expand_pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        instruction: str = "",
        transformer: Callable = None,
    ) -> None:
        """Create the application and apply keybindings."""
        self.content_control: InquirerPyExpandControl = InquirerPyExpandControl(
            choices, default, pointer, separator, help_msg, expand_pointer
        )
        super().__init__(message, style, editing_mode, qmark, instruction, transformer)

        def keybinding_factory(key):
            @self.kb.add(key.lower())
            def keybinding(_) -> None:
                if key == "h":
                    self.content_control.expanded = not self.content_control.expanded
                else:
                    self.content_control.selected_choice_index = (
                        self.content_control.key_maps[key]
                    )

            return keybinding

        for choice in self.content_control.choices:
            if not isinstance(choice["value"], Separator):
                keybinding_factory(choice["key"])

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up.

        Overriding this method to skip the help choice.
        """
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
            "(%s)" % "".join(self.content_control.key_maps.keys())
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
