"""Module contains base class for prompts."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, NamedTuple, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import IsDone
from prompt_toolkit.filters.base import Condition, FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.enum import ACCEPTED_KEYBINDINGS, INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import calculate_height


class BaseSimplePrompt(ABC):
    """The base class for simple prompts.

    Inherit this class to create a simple prompt that leverage `prompt_toolkit`
    PromptSession.

    Note: the PromptSession is not initialised in the constructor, require
    a call of `self.session = PromptSession(...)`.

    :param message: the question message to display
    :type message: str
    :param style: the style dictionary to apply
    :type style: Dict[str, str]
    :param default: set default answer to true
    :param qmark: the custom qmark to display infront of the question
    :type qmark: str
    :param validate: a callable or Validator instance to validate user input
    :type validate: Union[Callable[[str], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        qmark: str = "?",
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable = None,
    ) -> None:
        """Construct the base class for simple prompts."""
        self.message = message
        self.question_style = Style.from_dict(style)
        self.qmark = qmark
        self.status = {"answered": False, "result": None}
        self.kb = KeyBindings()
        self.lexer = "class:input"
        self.transformer = transformer
        self._invalid = False
        try:
            self.editing_mode = ACCEPTED_KEYBINDINGS[editing_mode]
        except KeyError:
            raise InvalidArgument(
                "editing_mode must be one of 'default' 'emacs' 'vim'."
            )
        if isinstance(validate, Validator):
            self.validator = validate
        else:
            self.validator = Validator.from_callable(
                validate if validate else lambda _: True,
                invalid_message,
                move_cursor_to_end=True,
            )

        @self.kb.add("c-c")
        def _(event) -> None:
            self.status["answered"] = True
            self.status["result"] = INQUIRERPY_KEYBOARD_INTERRUPT
            event.app.exit(result=INQUIRERPY_KEYBOARD_INTERRUPT)

    def _register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True
    ) -> Callable:
        """Decorate keybinding registration function.

        Ensure that invalid state is cleared on next
        keybinding entered.
        """

        def decorator(func: Callable) -> Callable:
            @self.kb.add(*keys, filter=filter)
            def executable(event):
                if self._invalid:
                    self._invalid = False
                return func(event)

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
                ("class:skipped", "%s %s " % (self.qmark, self.message))
            )
        else:
            display_message.append(("class:questionmark", self.qmark))
            display_message.append(("class:question", " %s" % self.message))
            if self.status["answered"]:
                display_message.append(
                    post_answer
                    if not self.transformer
                    else ("class:answer", " %s" % self.transformer(post_answer[1][1:]))
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
    :type choices: Union[Callable[[], List[Any]], List[Any]],
    :param default: default value, will impact the cursor position
    :type default: Any
    """

    def __init__(
        self,
        choices: Union[Callable[[], List[Any]], List[Any]],
        default: Any = None,
    ) -> None:
        """Initialise choices and construct a FormattedTextControl object."""
        self.selected_choice_index: int = 0
        self._choice_func = None
        self._default = default
        self._loading = False
        self._raw_choices = []
        if isinstance(choices, Callable):
            self._loading = True
            self.choices = []
            self._choice_func = choices
            self._loading = True
        else:
            self._raw_choices = choices
            self.choices = self._get_choices(choices, self._default)  # type: ignore
            self._safety_check()
        self._format_choices()
        super().__init__(self._get_formatted_choices)

    def _retrieve_choices(self) -> None:
        """Retrieve the callable choices and format them.

        Should be called in the `after_render` call in `Application`.
        """
        self._raw_choices = self._choice_func()  # type: ignore
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

    Consists of 2 horizontally splitted Window with one being the question and the second
    window responsible to dynamically generate the content.

    Upon entering the answer, update the first window's formatted text.

    :param message: question to display to the user
    :type message: str
    :param style: style to apply to the prompt
    :type style: Dict[str, str]
    :param editing_mode: controls the key_binding
    :type editing_mode: Literal["emacs", "default", "vim"]
    :param qmark: question mark to display
    :type qmark: str
    :param instruction: instruction to display after the question message
    :type instruction: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable
    :param height: preferred height of the choice window
    :type height: Union[str, int]
    :param max_height: max height choice window should reach
    :type max_height: Union[str, int]
    :param validate: a callable or Validator instance to validate user selection
    :type validate: Union[Callable[[str], bool], Validator]
    :param invalid_message: message to display when input is invalid
    :type invalid_message: str
    :param multiselect: enable multiselect mode
    :type multiselect: bool
    :param marker: marker symbol for selected choice
    :type marker: str
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        qmark: str = "?",
        instruction: str = "",
        transformer: Callable = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
    ) -> None:
        """Initialise the Application with Layout and keybindings."""
        super().__init__(
            message=message,
            style=style,
            editing_mode=editing_mode,
            qmark=qmark,
            transformer=transformer,
            invalid_message=invalid_message,
            validate=validate,
        )
        self._content_control: InquirerPyUIControl
        self._instruction = instruction
        self._invalid_message = invalid_message
        self._multiselect = multiselect
        self._rendered = False

        @Condition
        def is_multiselect() -> bool:
            return self._multiselect

        @Condition
        def is_vim_edit() -> bool:
            return self.editing_mode == EditingMode.VI

        @Condition
        def is_invalid() -> bool:
            return self._invalid

        @Condition
        def is_loading() -> bool:
            return self.content_control._loading

        @self._register_kb("down")
        @self._register_kb("c-n", filter=~is_vim_edit)
        @self._register_kb("j", filter=is_vim_edit)
        def _(event):
            self._handle_down()

        @self._register_kb("up")
        @self._register_kb("c-p", filter=~is_vim_edit)
        @self._register_kb("k", filter=is_vim_edit)
        def _(event):
            self._handle_up()

        @self._register_kb(" ", filter=is_multiselect)
        def _(event) -> None:
            self._toggle_choice()

        @self._register_kb(Keys.Tab, filter=is_multiselect)
        def _(event) -> None:
            self._toggle_choice()
            self._handle_down()

        @self._register_kb(Keys.BackTab, filter=is_multiselect)
        def _(event) -> None:
            self._toggle_choice()
            self._handle_up()

        @self._register_kb("escape", "a", filter=is_multiselect)
        def _(event) -> None:
            self._toggle_all(True)

        @self._register_kb("escape", "r", filter=is_multiselect)
        def _(event) -> None:
            self._toggle_all()

        @self._register_kb("enter")
        def _(event):
            self._handle_enter(event)

        dimmension_height, dimmension_max_height = calculate_height(height, max_height)
        self.layout = HSplit(
            [
                Window(
                    height=LayoutDimension.exact(1),
                    content=FormattedTextControl(
                        self._get_prompt_message, show_cursor=False
                    ),
                ),
                ConditionalContainer(
                    Window(
                        content=self.content_control,
                        height=Dimension(
                            max=dimmension_max_height, preferred=dimmension_height
                        ),
                    ),
                    filter=~IsDone() & ~is_loading,
                ),
                ConditionalContainer(
                    Window(
                        FormattedTextControl(
                            [("class:validation-toolbar", self._invalid_message)]
                        ),
                        dont_extend_height=True,
                    ),
                    filter=~IsDone() & is_invalid,
                ),
            ]
        )

        self.application = Application(
            layout=Layout(self.layout),
            style=self.question_style,
            key_bindings=self.kb,
            after_render=self._after_render,
        )

    def _after_render(self, _) -> None:
        """Render callable choices.

        Forcing a check on `self._rendered` as this event is fired up on each
        render, we only want this to fire up once.
        """
        if not self._rendered:
            self._rendered = True
            if self.content_control._choice_func:
                self.content_control._retrieve_choices()

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

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get the prompt message.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " %s" % self.instruction)
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> Any:
        """Execute the application and get the result."""
        return self.application.run()

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
            self.validator.validate(fake_document)  # type: ignore
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
            return self.content_control.selection["value"]

    @property
    def selected_choices(self) -> List[Any]:
        """Get all user selected choices.

        :return: list of selected/enabled choices
        :rtype: List[Any]
        """

        def filter_choice(choice):
            return not isinstance(choice, Separator) and choice["enabled"]

        return list(filter(filter_choice, self.content_control.choices))
