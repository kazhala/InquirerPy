"""Module contains base class for prompts."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import IsDone
from prompt_toolkit.filters.base import Condition
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import Validator

from InquirerPy.enum import ACCEPTED_KEYBINDINGS, INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


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
    :type choices: List[Any]
    :param default: default value, will impact the cursor position
    :type default: Any
    """

    def __init__(
        self,
        choices: List[Any],
        default: Any = None,
    ) -> None:
        """Initialise choices and construct a FormattedTextControl object."""
        self.selected_choice_index: int = 0
        self.choices: List[Dict[str, Any]] = self._get_choices(choices, default)
        self._safety_check()
        super().__init__(self._get_formatted_choices)

    def _get_choices(
        self, choices: List[Union[Any, Dict[str, Any]]], default: Any
    ) -> List[Dict[str, Any]]:
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
                        {"name": str(choice["name"]), "value": choice["value"]}
                    )
                elif isinstance(choice, Separator):
                    if self.selected_choice_index == index:
                        self.selected_choice_index = (
                            self.selected_choice_index + 1
                        ) % len(choices)
                    processed_choices.append({"name": str(choice), "value": choice})
                else:
                    if choice == default:
                        self.selected_choice_index = index
                    processed_choices.append({"name": str(choice), "value": choice})
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
        display_choices.pop()
        return display_choices

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
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        qmark: str = "?",
        instruction: str = "",
        transformer: Callable = None,
    ) -> None:
        """Initialise the Application with Layout and keybindings."""
        super().__init__(message, style, editing_mode, qmark, transformer=transformer)
        self._content_control: InquirerPyUIControl
        self._instruction = instruction
        self.layout = HSplit(
            [
                Window(
                    height=LayoutDimension.exact(1),
                    content=FormattedTextControl(
                        self._get_prompt_message, show_cursor=False
                    ),
                ),
                ConditionalContainer(
                    Window(content=self.content_control),
                    filter=~IsDone(),
                ),
            ]
        )

        @Condition
        def is_vim_edit() -> bool:
            return self.editing_mode == EditingMode.VI

        @self.kb.add("down")
        @self.kb.add("c-n", filter=~is_vim_edit)
        @self.kb.add("j", filter=is_vim_edit)
        def _(event):
            self._handle_down()

        @self.kb.add("up")
        @self.kb.add("c-p", filter=~is_vim_edit)
        @self.kb.add("k", filter=is_vim_edit)
        def _(event):
            self._handle_up()

        @self.kb.add("enter")
        def _(event):
            self._handle_enter(event)

        self.application = Application(
            layout=Layout(self.layout),
            style=self.question_style,
            key_bindings=self.kb,
        )

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
        """
        self.status["answered"] = True
        self.status["result"] = self.content_control.selection["name"]
        event.app.exit(result=self.content_control.selection["value"])
