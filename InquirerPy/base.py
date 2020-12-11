"""Module contains base class for prompts."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

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

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator


ACCEPTED_KEYBINDINGS: Dict[str, EditingMode] = {
    "default": EditingMode.EMACS,
    "emacs": EditingMode.EMACS,
    "vim": EditingMode.VI,
}

INQUIRERPY_KEYBOARD_INTERRUPT = "INQUIRERPY_KEYBOARD_INTERRUPT"

INQUIRERPY_POINTER_SEQUENCE = "\u276f"
INQUIRERPY_FILL_HEX_SEQUENCE = "\u2b22"
INQUIRERPY_EMPTY_HEX_SEQUENCE = "\u2b21"


class BaseSimplePrompt(ABC):
    """The base class for simple prompts.

    :param message: the question message to display
    :type message: str
    :param style: the style dictionary to apply
    :type style: Dict[str, str]
    :param default: set default answer to true
    :param symbol: the custom symbol to display infront of the question
    :type symbol: str
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        symbol: str = "?",
        validator: Optional[Union[Callable[[str], bool], Validator]] = None,
        invalid_message: str = "Invalid input",
    ) -> None:
        """Construct the base class for simple prompts."""
        self.message = message
        self.question_style = Style.from_dict(style)
        self.symbol = symbol
        self.status = {"answered": False, "result": None}
        self.kb = KeyBindings()
        self.lexer = "class:input"
        try:
            self.editing_mode = ACCEPTED_KEYBINDINGS[editing_mode]
        except KeyError:
            raise InvalidArgument(
                "editing_mode must be one of 'default' 'emacs' 'vim'."
            )
        if isinstance(validator, Validator):
            self.validator = validator
        else:
            self.validator = Validator.from_callable(
                validator if validator else lambda _: True,
                invalid_message,
                move_cursor_to_end=True,
            )

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
        """
        display_message = []
        display_message.append(("class:symbol", self.symbol))
        display_message.append(("class:question", " %s" % self.message))
        if self.status["answered"]:
            display_message.append(post_answer)
        else:
            display_message.append(pre_answer)
        return display_message

    @abstractmethod
    def execute(self) -> Any:
        """Abstractmethod to enforce a execute function is implemented for eaiser management."""
        pass


class InquirerPyUIControl(FormattedTextControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Dynamically adapt to user input and update formatted text.

    :param options: list of options to display as the content
    :type options: List[Any]
    :param default: default value, will impact the cursor position
    :type default: Any
    """

    def __init__(
        self,
        options: List[Any],
        default: Any = None,
    ) -> None:
        """Initialise options and construct a FormattedTextControl object."""
        self.selected_option_index: int = 0
        self.options: List[Dict[str, Any]] = self._get_options(options, default)
        self._safety_check()
        super().__init__(self._get_formatted_options)

    def _get_options(
        self, options: List[Union[Any, Dict[str, Any]]], default: Any
    ) -> List[Dict[str, Any]]:
        """Process the raw user input options and format it into dictionary.

        :param options: list of options to display
        :type options: List[Union[str, Dict[str, Any]]]
        :param default: default value, this affect selected_option_index
        :type default: Any
        :return: formatted options
        :rtype: List[Dict[str, Any]]
        """
        processed_options: List[Dict[str, Any]] = []
        try:
            for index, option in enumerate(options, start=0):
                if isinstance(option, dict):
                    if option["value"] == default:
                        self.selected_option_index = index
                    processed_options.append(
                        {"name": str(option["name"]), "value": option["value"]}
                    )
                elif isinstance(option, Separator):
                    if self.selected_option_index == index:
                        self.selected_option_index = (
                            self.selected_option_index + 1
                        ) % len(options)
                    processed_options.append({"name": str(option), "value": option})
                else:
                    if option == default:
                        self.selected_option_index = index
                    processed_options.append({"name": str(option), "value": option})
        except KeyError:
            raise RequiredKeyNotFound(
                "dictionary option require a name key and a value key."
            )
        return processed_options

    def _safety_check(self) -> None:
        """Validate options, check empty or all Separator."""
        if not self.options:
            raise InvalidArgument("options cannot be empty.")
        should_proceed: bool = False
        for option in self.options:
            if not isinstance(option["value"], Separator):
                should_proceed = True
                break
        if not should_proceed:
            raise InvalidArgument(
                "options should contain content other than separator."
            )

    def _get_formatted_options(self) -> List[Tuple[str, str]]:
        """Get all options in formatted text format.

        :return: a list of formatted options
        :rtype: List[Tuple[str, str]]
        """
        display_choices = []

        for index, option in enumerate(self.options):
            if index == self.selected_option_index:
                display_choices += self._get_hover_text(option)
            else:
                display_choices += self._get_normal_text(option)
            display_choices.append(("", "\n"))
        display_choices.pop()
        return display_choices

    @abstractmethod
    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        """Generate the formatted text for hovered option.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]
        """
        pass

    @abstractmethod
    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        """Generate the formatted text for non-hovered options.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]]
        """
        pass

    @property
    def option_count(self) -> int:
        """Get the option count.

        :return: total count of options
        :rtype: int
        """
        return len(self.options)

    @property
    def selection(self) -> Dict[str, Any]:
        """Get current selection value.

        :return: a dictionary of name and value for the current pointed option
        :rtype: Dict[str, Any]
        """
        return self.options[self.selected_option_index]


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
    :param symbol: question mark to display
    :type symbol: str
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = {},
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        symbol: str = "?",
    ) -> None:
        """Initialise the Application."""
        super().__init__(message, style, editing_mode, symbol)
        self._content_control: InquirerPyUIControl

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
            self.handle_down()

        @self.kb.add("up")
        @self.kb.add("c-p", filter=~is_vim_edit)
        @self.kb.add("k", filter=is_vim_edit)
        def _(event):
            self.handle_up()

        @self.kb.add("enter")
        def _(event):
            self.handle_enter(event)

        @self.kb.add("c-c")
        def _(event) -> None:
            self.status["answered"] = True
            self.status["result"] = ""
            event.app.exit(result=INQUIRERPY_KEYBOARD_INTERRUPT)

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

    @abstractmethod
    def handle_enter(self, event) -> None:
        """Handle the event when user hit Enter key.

        Require implementation at child classes.
        """
        pass

    @property
    @abstractmethod
    def instruction(self) -> str:
        """Instruction to display next to question.

        :return: instruction text
        :rtype: str
        """
        pass

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

    def handle_up(self) -> None:
        """Handle the event when user attempt to move up.

        Override this method for prompts that doesn't require moving up/down.
        """
        while True:
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index - 1
            ) % self.content_control.option_count
            if not isinstance(self.content_control.selection["value"], Separator):
                break

    def handle_down(self) -> None:
        """Handle the event when user attempt to move down.

        Override this method for prompts that doesn't require moving up/down.
        """
        while True:
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index + 1
            ) % self.content_control.option_count
            if not isinstance(self.content_control.selection["value"], Separator):
                break
