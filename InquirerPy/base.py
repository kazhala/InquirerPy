"""Module contains base class for prompts."""

from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgumentType


ACCEPTED_KEYBINDINGS: Dict[str, EditingMode] = {
    "default": EditingMode.EMACS,
    "emacs": EditingMode.EMACS,
    "vim": EditingMode.VI,
}


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
            raise InvalidArgumentType(
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

    def _get_prompt_message(
        self, pre_answer: Tuple[str, str], post_answer: Tuple[str, str]
    ) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Leveraging the nature of Dict in python, we can dynamically update the prompt
        message of the PromptSession.

        This is useful to format/customize user input for better visual.

        :param pre_answer: the information to display before answering the question
        :type pre_answer: str
        :param post_answer: the information to display after answering the question
        :type post_answer: str
        """
        display_message = []
        display_message.append(("class:symbol", self.symbol))
        display_message.append(("class:question", " %s " % self.message))
        if self.status["answered"]:
            display_message.append(post_answer)
        else:
            display_message.append(pre_answer)
        return display_message
