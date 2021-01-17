"""Module contains base class for prompts.

BaseSimplePrompt ← InputPrompt, 
        ↑               ↑
        ↑          SecretPrompt ...
        ↑
BaseComplexPrompt ← FuzzyPrompt
        ↑
BaseListPrompt ← ListPrompt, ExpandPrompt ...
"""
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import IsDone
from prompt_toolkit.filters.base import Condition, FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyBindings, KeyHandlerCallable
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult, calculate_height, get_style

__all__ = [
    "BaseSimplePrompt",
    "BaseComplexPrompt",
    "BaseListPrompt",
    "InquirerPyUIControl",
]


class BaseSimplePrompt(ABC):
    """The base class for simple prompts.

    Inherit this class to create a simple prompt that leverage `prompt_toolkit`
    PromptSession.

    Note: the PromptSession is not initialised in the constructor, require
    a call of `self.session = PromptSession(...)`.

    :param message: the question message to display
    :type message: Union[str, Callable[[SessionResult], str]]
    :param style: the style dictionary to apply
    :type style: InquirerPyStyle
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: str
    :param qmark: the custom qmark to display infront of the question
    :type qmark: str
    :param validate: a callable or Validator instance to validate user input
    :type validate: Union[Callable[[Any], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[Any], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    :param session_result: the current session result, this is used by callable message and choices
        to generate dynamic values. If using alternate syntax, skip this value.
    :type session_result: SessionResult
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        session_result: SessionResult = None,
        default: Any = "",
    ) -> None:
        """Construct the base class for simple prompts."""
        self._result = session_result or {}
        self._message = message if not isinstance(message, Callable) else message(self._result)  # type: ignore
        self._default = (
            default if not isinstance(default, Callable) else default(self._result)
        )
        self._style = Style.from_dict(style.dict if style else get_style().dict)
        self._qmark = qmark
        self._status = {"answered": False, "result": None}
        self._kb = KeyBindings()
        self._lexer = "class:input"
        self._transformer = transformer
        self._filter = filter
        self._editing_mode = (
            EditingMode.VI
            if vi_mode or bool(os.getenv("INQUIRERPY_VI_MODE", False))
            else EditingMode.EMACS
        )
        if isinstance(validate, Validator):
            self._validator = validate
        else:
            self._validator = Validator.from_callable(
                validate if validate else lambda _: True,
                invalid_message,
                move_cursor_to_end=True,
            )

        @self._kb.add("c-c")
        def _(event) -> None:
            self.status["answered"] = True
            self.status["result"] = INQUIRERPY_KEYBOARD_INTERRUPT
            event.app.exit(result=INQUIRERPY_KEYBOARD_INTERRUPT)

    @property
    def status(self) -> Dict[str, Any]:
        """Get status value of the prompt."""
        return self._status

    @status.setter
    def status(self, value) -> None:
        """Set status value of the prompt."""
        self._status = value

    def register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True
    ) -> Callable[[KeyHandlerCallable], KeyHandlerCallable]:
        """Decorate keybinding registration function.

        Format all alt related keybindings.

        Due to `prompt_toolkit` doesn't process alt related keybindings,
        it requires alt-ANY to "escape" + "ANY".

        Check a list of keys argument if they are alt related, change
        them to escape.

        :param keys: keys to bind into the keybindings
        :type keys: Union[Keys, str]
        :param filter: condition of whether this keybinding should be active
        :type filter: FilterOrBool
        :return: a decorator that should be applied to the function thats intended
            to be active when the keys being pressed
        :rtype: Callable[[KeyHandlerCallable], KeyHandlerCallable]
        """
        alt_pattern = re.compile(r"^alt-(.*)")

        def decorator(func: KeyHandlerCallable) -> KeyHandlerCallable:
            formatted_keys = []
            for key in keys:
                match = alt_pattern.match(key)
                if match:
                    formatted_keys.append("escape")
                    formatted_keys.append(match.group(1))
                else:
                    formatted_keys.append(key)

            @self._kb.add(*formatted_keys, filter=filter)
            def executable(event) -> None:
                func(event)

            return executable

        return decorator

    @abstractmethod
    def _get_prompt_message(
        self, pre_answer: Tuple[str, str], post_answer: Tuple[str, str]
    ) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Leveraging the nature of Dict in python, we can dynamically update the prompt
        message of the PromptSession.

        This is useful to format/customize user input for better visual.

        :param pre_answer: the information to display before answering the question
        :type pre_answer: Tuple[str, str]
        :param post_answer: the information to display after answering the question
        :type post_answer: Tuple[str, str]
        :return: formatted text thats ready to be consumed by PromptSession
        :rtype: List[Tuple[str, str]]
        """
        display_message = []
        if self.status["result"] == INQUIRERPY_KEYBOARD_INTERRUPT:
            display_message.append(
                ("class:skipped", "%s %s " % (self._qmark, self._message))
            )
        else:
            display_message.append(("class:questionmark", self._qmark))
            display_message.append(("class:question", " %s" % self._message))
            if self.status["answered"]:
                display_message.append(
                    post_answer
                    if not self._transformer
                    else (
                        "class:answer",
                        " %s" % self._transformer(self.status["result"]),
                    )
                )
            else:
                display_message.append(pre_answer)
        return display_message

    @abstractmethod
    def execute(self) -> Any:
        """Abstractmethod to enforce a execute function is implemented for eaiser management.

        All prompt instance require a execute call to initialised the `PromptSession` or `Application`.
        This is being called in the resolver.
        """
        pass


class InquirerPyUIControl(FormattedTextControl):
    """A UIControl class intended to be consumed by `prompt_toolkit` window.

    Dynamically adapt to user input and update formatted text.

    :param choices: list of choices to display as the content
    :type choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
    :param default: default value, will impact the cursor position
    :type default: Any
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise choices and construct a FormattedTextControl object."""
        self._session_result = session_result or {}
        self._selected_choice_index: int = 0
        self._choice_func = None
        self._loading = False
        self._raw_choices = []
        self._default = (
            default
            if not isinstance(default, Callable)
            else default(self._session_result)
        )
        if isinstance(choices, Callable):
            self._loading = True
            self._choices = []
            self._choice_func = choices
            self._loading = True
        else:
            self._raw_choices = choices
            self._choices = self._get_choices(choices, self._default)  # type: ignore
            self._safety_check()
        self._format_choices()
        super().__init__(self._get_formatted_choices)

    def _retrieve_choices(self) -> None:
        """Retrieve the callable choices and format them.

        Should be called in the `after_render` call in `Application`.

        :param session_result: the current result of the prompt session,
            if using alternate syntax, skip this value
        :type session_result: SessionResult
        """
        self._raw_choices = self._choice_func(self._session_result)  # type: ignore
        self.choices = self._get_choices(self._raw_choices, self._default)
        self._loading = False
        self._safety_check()
        self._format_choices()

    def _get_choices(self, choices: List[Any], default: Any) -> List[Dict[str, Any]]:
        """Process the raw user input choices and format it into dictionary.

        :param choices: list of choices to display
        :type choices: List[Union[str, Dict[str, Any]]]
        :param default: default value, this affect selected_choice_index
        :type default: Any
        :return: formatted choices
        :rtype: List[Dict[str, Any]]
        """
        processed_choices: List[Dict[str, Any]] = []
        try:
            for index, choice in enumerate(choices, start=0):
                if isinstance(choice, dict):
                    if choice["value"] == default:
                        self.selected_choice_index = index
                    processed_choices.append(
                        {
                            "name": str(choice["name"]),
                            "value": choice["value"],
                            "enabled": False,
                        }
                    )
                elif isinstance(choice, Separator):
                    if self.selected_choice_index == index:
                        self.selected_choice_index = (
                            self.selected_choice_index + 1
                        ) % len(choices)
                    processed_choices.append(
                        {"name": str(choice), "value": choice, "enabled": False}
                    )
                else:
                    if choice == default:
                        self.selected_choice_index = index
                    processed_choices.append(
                        {"name": str(choice), "value": choice, "enabled": False}
                    )
        except KeyError:
            raise RequiredKeyNotFound(
                "dictionary choice require a name key and a value key."
            )
        return processed_choices

    @property
    def selected_choice_index(self) -> int:
        """Get current highlighted index."""
        return self._selected_choice_index

    @selected_choice_index.setter
    def selected_choice_index(self, value) -> None:
        """Set index to highlight."""
        self._selected_choice_index = value

    @property
    def choices(self) -> List[Dict[str, Any]]:
        """Get all processed choices."""
        return self._choices

    @choices.setter
    def choices(self, value) -> None:
        """Set processed choices."""
        self._choices = value

    def _safety_check(self) -> None:
        """Validate choices, check empty or all Separator."""
        if not self.choices:
            raise InvalidArgument("choices cannot be empty.")
        should_proceed: bool = False
        for choice in self.choices:
            if not isinstance(choice["value"], Separator):
                should_proceed = True
                break
        if not should_proceed:
            raise InvalidArgument(
                "choices should contain content other than separator."
            )

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Get all choices in formatted text format.

        :return: a list of formatted choices
        :rtype: List[Tuple[str, str]]
        """
        display_choices = []

        for index, choice in enumerate(self.choices):
            if index == self.selected_choice_index:
                display_choices += self._get_hover_text(choice)
            else:
                display_choices += self._get_normal_text(choice)
            display_choices.append(("", "\n"))
        if display_choices:
            display_choices.pop()
        return display_choices

    @abstractmethod
    def _format_choices(self) -> None:
        """Perform post processing on the choices.

        Customise the choices after `self._get_choices` call.
        """
        pass

    @abstractmethod
    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for hovered choice.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]
        """
        pass

    @abstractmethod
    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for non-hovered choices.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]]
        """
        pass

    @property
    def choice_count(self) -> int:
        """Get the choice count.

        :return: total count of choices
        :rtype: int
        """
        return len(self.choices)

    @property
    def selection(self) -> Dict[str, Any]:
        """Get current selection value.

        :return: a dictionary of name and value for the current pointed choice
        :rtype: Dict[str, Any]
        """
        return self.choices[self.selected_choice_index]


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
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
        keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
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
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            session_result=session_result,
        )
        self._content_control: InquirerPyUIControl
        self._instruction = instruction
        self._invalid_message = invalid_message
        self._multiselect = multiselect
        self._rendered = False
        self._invalid = False
        self._application: Application

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

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " %s" % self.instruction)
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self, raise_keyboard_interrupt: bool = True) -> Any:
        """Execute the application and get the result.

        :param raise_keyboard_interrupt: raise kbi exception when user hit 'c-c'
        :type raise_keyboard_interrupt: bool
        :return: user selected value
        :rtype: Any
        """
        result = self.application.run()
        if result == INQUIRERPY_KEYBOARD_INTERRUPT:
            if raise_keyboard_interrupt and not os.getenv(
                "INQUIRERPY_NO_RAISE_KBI", False
            ):
                raise KeyboardInterrupt
            else:
                result = None
        if not self._filter:
            return result
        return self._filter(result)

    @property
    def instruction(self) -> str:
        """Instruction to display next to question.

        :return: instruction text
        :rtype: str
        """
        return self._instruction

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

        :return: list of selected/enabled choices
        :rtype: List[Any]
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

    @abstractmethod
    def _handle_enter(self, event) -> None:
        """Handle event when user input enter key."""
        pass

    @abstractmethod
    def _handle_down(self) -> None:
        """Handle event when user attempting to move down."""
        pass

    @abstractmethod
    def _handle_up(self) -> None:
        """Handle event when user attempting to move down."""
        pass

    @abstractmethod
    def _toggle_choice(self) -> None:
        """Handle event when user attempting to toggle the state of the chocie."""
        pass

    @abstractmethod
    def _toggle_all(self, value: bool) -> None:
        """Handle event when user attempting to alter the state of all choices."""
        pass


class BaseListPrompt(BaseComplexPrompt):
    """A base class to create a complex prompt using `prompt_toolkit` Application.

    Consists of 2 horizontally splitted Window with one being the question and the second
    window responsible to dynamically generate the content.

    Upon entering the answer, update the first window's formatted text.

    :param message: question to display to the user
    :type message: Union[str, Callable[[SessionResult], str]]
    :param style: style to apply to the prompt
    :type style: InquirerPyStyle
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: bool
    :param qmark: question mark to display
    :type qmark: str
    :param instruction: instruction to display after the question message
    :type instruction: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[Any], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
    :param validate: a callable or Validator instance to validate user selection
    :type validate: Union[Callable[[Any], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param multiselect: enable multiselect mode
    :type multiselect: bool
    :param keybindings: custom keybindings to apply
    :type keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]]
    :param show_cursor: display cursor at the end of the prompt
    :type show_cursor: bool
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
        keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
        show_cursor: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the Application with Layout and keybindings."""
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            multiselect=multiselect,
            instruction=instruction,
            keybindings=keybindings,
            session_result=session_result,
        )
        self._dimmension_height, self._dimmension_max_height = calculate_height(
            height, max_height
        )

        self.layout = HSplit(
            [
                Window(
                    height=LayoutDimension.exact(1),
                    content=FormattedTextControl(
                        self._get_prompt_message_with_cursor
                        if show_cursor
                        else self._get_prompt_message,
                        show_cursor=show_cursor,
                    ),
                ),
                ConditionalContainer(
                    Window(
                        content=self.content_control,
                        height=Dimension(
                            max=self._dimmension_max_height,
                            preferred=self._dimmension_height,
                        ),
                        dont_extend_height=True,
                    ),
                    filter=~IsDone() & ~self._is_loading,
                ),
                ConditionalContainer(
                    Window(FormattedTextControl([("", "")])),
                    filter=~IsDone(),  # force validation bar to stay bottom
                ),
                ConditionalContainer(
                    Window(
                        FormattedTextControl(
                            [
                                (
                                    "class:validation-toolbar",
                                    self._invalid_message,
                                )
                            ]
                        ),
                        dont_extend_height=True,
                    ),
                    filter=self._is_invalid & ~IsDone(),
                ),
            ]
        )

        self.application = Application(
            layout=Layout(self.layout),
            style=self._style,
            key_bindings=self._kb,
            after_render=self._after_render,
        )

    def _get_prompt_message_with_cursor(self) -> List[Tuple[str, str]]:
        """Obtain the prompt message to display.

        Introduced a new method instead of using the `_get_prompt_message`
        due to `expand` and `rawlist` make changes after calling `super()._get_prompt_message()`.

        This ensures that cursor is always at the end of the window no matter
        when the changes is made to the `_get_prompt_message`.
        """
        message = self._get_prompt_message()
        message.append(("[SetCursorPosition]", ""))
        message.append(("", " "))  # [SetCursorPosition] require char behind it
        return message

    def _toggle_choice(self) -> None:
        """Toggle the `enabled` status of the choice."""
        self.content_control.selection["enabled"] = not self.content_control.selection[
            "enabled"
        ]

    def _toggle_all(self, value: bool = None) -> None:
        """Toggle all choice `enabled` status.

        :param value: sepcify a value to toggle
        :type value: bool
        """
        for choice in self.content_control.choices:
            if isinstance(choice["value"], Separator):
                continue
            choice["enabled"] = value if value else not choice["enabled"]

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up."""
        while True:
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index - 1
            ) % self.content_control.choice_count
            if not isinstance(self.content_control.selection["value"], Separator):
                break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down."""
        while True:
            self.content_control.selected_choice_index = (
                self.content_control.selected_choice_index + 1
            ) % self.content_control.choice_count
            if not isinstance(self.content_control.selection["value"], Separator):
                break

    def _handle_enter(self, event) -> None:
        """Handle the event when user hit Enter key.

        * Set the state to answered for an update to the prompt display.
        * Set the result to user selected choice's name for display purpose.
        * Let the app exit with the user selected choice's value and return the actual value back to resolver.

        In multiselect scenario, if nothing is selected, return the current highlighted choice.
        """
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
        except ValidationError:
            self._invalid = True
        else:
            self.status["answered"] = True
            if self._multiselect and not self.selected_choices:
                self.status["result"] = [self.content_control.selection["name"]]
                event.app.exit(result=[self.content_control.selection["value"]])
            else:
                self.status["result"] = self.result_name
                event.app.exit(result=self.result_value)
