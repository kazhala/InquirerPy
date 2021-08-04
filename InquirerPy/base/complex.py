"""Contains the interface class for list type prompts and the mocked document class `FakeDocument`."""
import shutil
from abc import abstractmethod
from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import Condition, FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyHandlerCallable
from prompt_toolkit.keys import Keys
from prompt_toolkit.validation import Validator

from InquirerPy.base.control import InquirerPyUIControl
from InquirerPy.base.simple import BaseSimplePrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult


class FakeDocument(NamedTuple):
    """A fake `prompt_toolkit` document class.

    Work around to allow non buffer type content_control to use the same
    `Validator` class.
    """

    text: str


class BaseComplexPrompt(BaseSimplePrompt):
    """A base class to create a complex prompt using `prompt_toolkit` Application.

    This class does not create `Layout` nor `Application`, it just contains helper
    functions to create a more complex prompt than the `BaseSimplePrompt`.

    Use `BaseListPrompt` to create a complex list prompt.

    Reference parameters through `BaseListPrompt` or `FuzzyPrompt`.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
        keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
        cycle: bool = True,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the Application with Layout and keybindings."""
        if not keybindings:
            keybindings = {}
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            wrap_lines=wrap_lines,
            session_result=session_result,
        )
        self._content_control: InquirerPyUIControl
        self._invalid_message = invalid_message
        self._multiselect = multiselect
        self._rendered = False
        self._invalid = False
        self._application: Application
        self._cycle = cycle

        @Condition
        def is_multiselect() -> bool:
            return self._multiselect

        @Condition
        def is_vim_edit() -> bool:
            return self._editing_mode == EditingMode.VI

        @Condition
        def is_invalid() -> bool:
            return self._invalid

        @Condition
        def is_loading() -> bool:
            return self.content_control._loading

        self._is_multiselect = is_multiselect
        self._is_vim_edit = is_vim_edit
        self._is_invalid = is_invalid
        self._is_loading = is_loading

        self._kb_maps = {
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
            ],
            "toggle-all-true": [
                {"key": "alt-a"},
            ],
            "toggle-all-false": [],
            **keybindings,
        }

        self._kb_func_lookup = {
            "down": [{"func": self._handle_down}],
            "up": [{"func": self._handle_up}],
            "toggle": [{"func": self._toggle_choice}],
            "toggle-down": [{"func": self._toggle_choice}, {"func": self._handle_down}],
            "toggle-up": [{"func": self._toggle_choice}, {"func": self._handle_up}],
            "toggle-all": [{"func": self._toggle_all}],
            "toggle-all-true": [{"func": self._toggle_all, "args": [True]}],
            "toggle-all-false": [{"func": self._toggle_all, "args": [False]}],
        }
        self._non_multiselect_action = {"down", "up"}

        def keybinding_factory(keys, filter, action):
            if not isinstance(keys, list):
                keys = [keys]
            if action not in self._non_multiselect_action:
                filter = filter & self._multiselect

            @self._register_kb(*keys, filter=filter)
            def _(event):
                for method in self._kb_func_lookup[action]:
                    method["func"](*method.get("args", []))

        for key, item in self._kb_maps.items():
            for kb in item:
                keybinding_factory(kb["key"], kb.get("filter", True), key)

        @self._register_kb("enter")
        def _(event):
            self._handle_enter(event)

    def _register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True
    ) -> Callable[[KeyHandlerCallable], KeyHandlerCallable]:
        """Decorate keybinding registration function.

        Ensure that invalid state is cleared on next
        keybinding entered.
        """

        def decorator(func: KeyHandlerCallable) -> KeyHandlerCallable:
            @self.register_kb(*keys, filter=filter)
            def executable(event):
                if self._invalid:
                    self._invalid = False
                func(event)

            return executable

        return decorator

    def _after_render(self, _) -> None:
        """Render callable choices.

        Forcing a check on `self._rendered` as this event is fired up on each
        render, we only want this to fire up once.
        """
        if not self._rendered:
            self._rendered = True
            if self.content_control._choice_func:
                self.content_control._retrieve_choices()

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get the prompt message.

        :return: List of formatted text.
        """
        pre_answer = (
            "class:instruction",
            " %s " % self.instruction if self.instruction else " ",
        )
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def _run(self) -> Any:
        return self.application.run()

    @property
    def content_control(self) -> InquirerPyUIControl:
        """Get the content controller object.

        Needs to be an instance of InquirerPyUIControl.
        """
        if not self._content_control:
            raise NotImplementedError
        return self._content_control

    @content_control.setter
    def content_control(self, value: InquirerPyUIControl) -> None:
        """Setter of content_control."""
        self._content_control = value

    @property
    def result_name(self) -> Any:
        """Get the result name of the application.

        In multiselect scenario, return result as a list.
        """
        if self._multiselect:
            return [choice["name"] for choice in self.selected_choices]
        else:
            return self.content_control.selection["name"]

    @property
    def result_value(self) -> Any:
        """Get the result value of the application.

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
        """Get all user selected choices.

        :return: List of selected/enabled choices.
        """

        def filter_choice(choice):
            return not isinstance(choice, Separator) and choice["enabled"]

        return list(filter(filter_choice, self.content_control.choices))

    @property
    def application(self) -> Application:
        """Get application.

        Require `self._application` to be defined since this class
        doesn't implement `Layout` and `Application`.
        """
        if not self._application:
            raise NotImplementedError
        return self._application

    @application.setter
    def application(self, value: Application) -> None:
        """Setter for `self._application`."""
        self._application = value

    def _handle_down(self) -> bool:
        """Handle event when user attempting to move down.

        :return: Boolean indicating if the action hits the cap.
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

    def _handle_up(self) -> bool:
        """Handle event when user attempting to move down.

        :return: Boolean indicating if the action hits the cap.
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
    def _handle_enter(self, event) -> None:
        """Handle event when user input enter key."""
        pass

    @abstractmethod
    def _toggle_choice(self) -> None:
        """Handle event when user attempting to toggle the state of the chocie."""
        pass

    @abstractmethod
    def _toggle_all(self, value: bool) -> None:
        """Handle event when user attempting to alter the state of all choices."""
        pass

    @property
    def total_message_length(self) -> int:
        """Get total width of the message row.

        :return: Mesage length.
        """
        total_message_length = 0
        if self._qmark:
            total_message_length += len(self._qmark)
            total_message_length += 1  # Extra space if qmark is present
        total_message_length += len(str(self._message))
        total_message_length += 1  # Extra space between message and instruction
        total_message_length += len(str(self._instruction))
        if self._instruction:
            total_message_length += 1  # Extra space behind the instruction
        return total_message_length

    @property
    def wrap_lines_offset(self) -> int:
        """Get extra offset due to line wrapping.

        :return: Extra offset.
        """
        if not self._wrap_lines:
            return 0
        term_width, _ = shutil.get_terminal_size()
        return self.total_message_length // term_width
