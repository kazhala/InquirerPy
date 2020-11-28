"""Module contains base class for prompts."""

from abc import abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound


ACCEPTED_KEYBINDINGS: Dict[str, EditingMode] = {
    "default": EditingMode.EMACS,
    "emacs": EditingMode.EMACS,
    "vim": EditingMode.VI,
}

INQUIRERPY_KEYBOARD_INTERRUPT = "INQUIRERPY_KEYBOARD_INTERRUPT"

INQUIRERPY_POINTER_SEQUENCE = "\u276f"


class BaseSimplePrompt:
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
        style: Dict[str, str],
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
        display_message.append(("class:question", " %s " % self.message))
        if self.status["answered"]:
            display_message.append(post_answer)
        else:
            display_message.append(pre_answer)
        return display_message


class InquirerPyUIControl(FormattedTextControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Dynamically adapt to user input and update formatted text

    :param options: list of options to display as the content
    :type options: List[Union[str, Dict[str, Any]]]
    :param default: default value, will impact the cursor position
    :type default: Any
    """

    def __init__(
        self,
        options: List[Union[str, Dict[str, Any]]],
        default: Any,
    ) -> None:
        """Initialise options and construct a FormattedTextControl object."""
        self.selected_option_index: int = 0
        self.options: List[Dict[str, Any]] = self._get_options(options, default)
        if not options:
            raise InvalidArgument("options cannot be empty.")
        super().__init__(self._get_formatted_options)

    def _get_options(
        self, options: List[Union[str, Dict[str, Any]]], default: Any
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
                if isinstance(option, str):
                    if option == default:
                        self.selected_option_index = index
                    processed_options.append({"name": option, "value": option})
                elif isinstance(option, dict):
                    if option["value"] == default:
                        self.selected_option_index = index
                    processed_options.append(
                        {"name": option["name"], "value": option["value"]}
                    )
                else:
                    raise InvalidArgument(
                        "each option has to be either a string or dictionary."
                    )
        except KeyError:
            raise RequiredKeyNotFound(
                "dictionary option require a name key and a value key."
            )
        except InvalidArgument:
            raise
        return processed_options

    def _get_formatted_options(self) -> List[Tuple[str, str]]:
        """Get all choice in formatted text format.

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
        """Generate the formatted text for hovered option."""
        pass

    @abstractmethod
    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        """Generate the formatted text for non-hovered options."""
        pass

    @property
    def option_count(self) -> int:
        """Get the option count."""
        return len(self.options)

    @property
    def selection(self) -> Any:
        """Get current selection value."""
        return self.options[self.selected_option_index]["value"]
