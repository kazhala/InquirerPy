"""Contains the base class :class:`.BaseListPrompt` which can be used to create a prompt involving choices."""
from abc import abstractmethod
from typing import Any, Callable, List, Optional

from prompt_toolkit.filters.base import Condition
from prompt_toolkit.keys import Keys

from InquirerPy.base.complex import BaseComplexPrompt
from InquirerPy.base.control import InquirerPyUIListControl
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyKeybindings,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)


class BaseListPrompt(BaseComplexPrompt):
    """A base class to create a complex prompt involving choice selections (i.e. list) using `prompt_toolkit` Application.

    Note:
        This class does not create :class:`~prompt_toolkit.layout.Layout` nor :class:`~prompt_toolkit.application.Application`,
        it only contains the necessary attributes and helper functions to be consumed.

    See Also:
        :class:`~InquirerPy.prompts.list.ListPrompt`
        :class:`~InquirerPy.prompts.fuzzy.FuzzyPrompt`
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        border: bool = False,
        transformer: Optional[Callable[[Any], Any]] = None,
        filter: Optional[Callable[[Any], Any]] = None,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
        keybindings: Optional[InquirerPyKeybindings] = None,
        cycle: bool = True,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            border=border,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            instruction=instruction,
            long_instruction=long_instruction,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
        )

        self._content_control: InquirerPyUIListControl
        self._multiselect = multiselect
        self._is_multiselect = Condition(lambda: self._multiselect)
        self._cycle = cycle

        if not keybindings:
            keybindings = {}

        self.kb_maps = {
            "down": [
                {"key": "down"},
                {"key": "c-n", "filter": ~self._is_vim_edit},
                {"key": "j", "filter": self._is_vim_edit},
            ],
            "up": [
                {"key": "up"},
                {"key": "c-p", "filter": ~self._is_vim_edit},
                {"key": "k", "filter": self._is_vim_edit},
            ],
            "toggle": [
                {"key": "space"},
            ],
            "toggle-down": [
                {"key": Keys.Tab},
            ],
            "toggle-up": [
                {"key": Keys.BackTab},
            ],
            "toggle-all": [
                {"key": "alt-r"},
                {"key": "c-r"},
            ],
            "toggle-all-true": [
                {"key": "alt-a"},
                {"key": "c-a"},
            ],
            "toggle-all-false": [],
            **keybindings,
        }

        self.kb_func_lookup = {
            "down": [{"func": self._handle_down}],
            "up": [{"func": self._handle_up}],
            "toggle": [{"func": self._handle_toggle_choice}],
            "toggle-down": [
                {"func": self._handle_toggle_choice},
                {"func": self._handle_down},
            ],
            "toggle-up": [
                {"func": self._handle_toggle_choice},
                {"func": self._handle_up},
            ],
            "toggle-all": [{"func": self._handle_toggle_all}],
            "toggle-all-true": [{"func": self._handle_toggle_all, "args": [True]}],
            "toggle-all-false": [{"func": self._handle_toggle_all, "args": [False]}],
        }

    @property
    def content_control(self) -> InquirerPyUIListControl:
        """Get the content controller object.

        Needs to be an instance of :class:`~InquirerPy.base.control.InquirerPyUIListControl`.

        Each :class:`.BaseComplexPrompt` requires a `content_control` to display custom
        contents for the prompt.

        Raises:
            NotImplementedError: When `self._content_control` is not found.
        """
        if not self._content_control:
            raise NotImplementedError
        return self._content_control

    @content_control.setter
    def content_control(self, value: InquirerPyUIListControl) -> None:
        self._content_control = value

    @property
    def result_name(self) -> Any:
        """Get the result value that should be printed to the terminal.

        In multiselect scenario, return result as a list.
        """
        if self._multiselect:
            return [choice["name"] for choice in self.selected_choices]
        else:
            try:
                return self.content_control.selection["name"]
            except IndexError:
                return ""

    @property
    def result_value(self) -> Any:
        """Get the result value that should return to the user.

        In multiselect scenario, return result as a list.
        """
        if self._multiselect:
            return [choice["value"] for choice in self.selected_choices]
        else:
            try:
                return self.content_control.selection["value"]
            except IndexError:
                return ""

    @property
    def selected_choices(self) -> List[Any]:
        """List[Any]: Get all user selected choices."""

        def filter_choice(choice):
            return not isinstance(choice, Separator) and choice["enabled"]

        return list(filter(filter_choice, self.content_control.choices))

    def _handle_down(self, _) -> bool:
        """Handle event when user attempts to move down.

        Returns:
            Boolean indicating if the action hits the cap.
        """
        if self._cycle:
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index + 1
            ) % self.content_control.choice_count
            return False
        else:
            self.content_control.selected_choice_index += 1
            if (
                self.content_control.selected_choice_index
                >= self.content_control.choice_count
            ):
                self.content_control.selected_choice_index = (
                    self.content_control.choice_count - 1
                )
                return True
            return False

    def _handle_up(self, _) -> bool:
        """Handle event when user attempts to move up.

        Returns:
            Boolean indicating if the action hits the cap.
        """
        if self._cycle:
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index - 1
            ) % self.content_control.choice_count
            return False
        else:
            self.content_control.selected_choice_index -= 1
            if self.content_control.selected_choice_index < 0:
                self.content_control.selected_choice_index = 0
                return True
            return False

    @abstractmethod
    def _handle_toggle_choice(self, event) -> None:
        """Handle event when user attempting to toggle the state of the chocie."""
        pass

    @abstractmethod
    def _handle_toggle_all(self, event, value: bool) -> None:
        """Handle event when user attempting to alter the state of all choices."""
        pass
