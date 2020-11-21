"""Module contains the class to create a secret prompt."""
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers.base import SimpleLexer
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgumentType


class Secret(BaseSimplePrompt):
    """A wrapper class around PromptSession to create a secret prompt.

    :param message: the message to display in the prompt
    :type message: str
    :param style: style to apply to the prompt
    :type style: Dict[str, str]
    :param default: the default value
    :type default: str
    :param symbol: symbol to display infront of the question
    :type symbol: str
    :param editing_mode: the key binding mode to use
    :type editing_mode: Literal["default", "vim", "emacs"]
    :param validator: a callable to validate the user input
    :type validator: Optional[Union[Validator, Callable[[str], bool]]]
    :param invalid_message: the error message to display when validator failed
    :type invalid_message: str
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str],
        default: str = "",
        symbol: str = "?",
        editing_mode: Literal["default", "vim", "emacs"] = "default",
        validator: Optional[Union[Validator, Callable[[str], bool]]] = None,
        invalid_message: str = "Invalid input",
        **kwargs
    ) -> None:
        """Construct the prompt session."""
        super().__init__(
            message,
            style,
            editing_mode,
            symbol,
            validator=validator,
            invalid_message=invalid_message,
        )
        self.default = default
        if not isinstance(self.default, str):
            raise InvalidArgumentType(
                "default for filepath type question should be type of str."
            )

        @self.kb.add(Keys.Enter)
        def _(event):
            try:
                self.session.validator.validate(self.session.default_buffer)
            except ValidationError:
                self.session.default_buffer.validate_and_handle()
            else:
                self.status["answered"] = True
                self.status["result"] = self.session.default_buffer.text
                self.session.default_buffer.text = ""
                event.app.exit(result=self.status["result"])

        self.session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self.kb,
            is_password=True,
            style=self.question_style,
            validator=self.validator,
            validate_while_typing=False,
            editing_mode=self.editing_mode,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
            lexer=SimpleLexer("class:input"),
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get formatted message to display in prompt.

        :return: a list of formatted message
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " ")
        post_answer = (
            "class:answer",
            ""
            if not self.status["result"]
            else "".join(["*" for _ in self.status["result"]]),
        )
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> None:
        """Execute the prompt."""
        return self.session.prompt(default=self.default)
