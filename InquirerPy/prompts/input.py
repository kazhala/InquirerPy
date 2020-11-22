"""Module contains the class to create an input prompt."""
from typing import Callable, Dict, List, Literal, Optional, Tuple, Union

from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion.base import Completer
from prompt_toolkit.filters import Condition
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgumentType


class InputPrompt(BaseSimplePrompt):
    """A wrapper class around PromptSession.

    This class is used for input prompt.

    :param message: the question to ask
    :type message: str
    :param style: a dictionary of style to apply
    :type style: Dict[str, str]
    :param editing_mode: the mode of editing
    :type editing_mode: Literal['default', 'emacs', 'vim']
    :param default: the default result
    :type default: str
    :param symbol: question symbol to display
    :type symbol: str
    :param completer: add auto completer to user input
    :type completer: Optional[Union[Dict[str, str], Completer]]
    :param validator: a callable or a validation class to validate user input
    :type validator: Optional[Union[Callable[[str], bool], Validator]]
    :param invalid_message: the error message to display when input is invalid
    :type invalid_message: str
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str],
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        default: str = "",
        symbol: str = "?",
        completer: Optional[Union[Dict[str, str], Completer]] = None,
        validator: Optional[Union[Callable[[str], bool], Validator]] = None,
        invalid_message: str = "Invalid input",
        **kwargs,
    ) -> None:
        """Construct a PromptSession based on parameters and apply key_bindings."""
        super().__init__(
            message,
            style,
            editing_mode=editing_mode,
            symbol=symbol,
            validator=validator,
            invalid_message=invalid_message,
        )
        self.default = default
        if not isinstance(self.default, str):
            raise InvalidArgumentType(
                "default for input type question should be type of str."
            )
        self.completer = None
        if isinstance(completer, dict):
            self.completer = NestedCompleter.from_nested_dict(completer)
        elif isinstance(completer, Completer):
            self.completer = completer

        @Condition
        def has_completion():
            return self.completer != None

        @self.kb.add("c-space", filter=has_completion)
        def _(event):
            buff = event.app.current_buffer
            if buff.complete_state:
                buff.complete_next()
            else:
                buff.start_completion(select_first=False)

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
            style=self.question_style,
            completer=self.completer,
            validator=self.validator,
            validate_while_typing=False,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
            editing_mode=self.editing_mode,
            lexer=SimpleLexer(self.lexer),
        )

    def _get_prompt_message(
        self,
        pre_answer: Optional[Tuple[str, str]] = None,
        post_answer: Optional[Tuple[str, str]] = None,
    ) -> List[Tuple[str, str]]:
        """Dynamically update the prompt message.

        Change the user input path to the 'answer' color in style.

        :param pre_answer: the formatted text to display before answering the question
        :type pre_answer: Optional[Tuple[str, str]]
        :param post_answer: the formatted text to display after answering the question
        :type post_answer: Optional[Tuple[str, str]]
        :return: the formatted text for PromptSession
        :rtype: List[Tuple[str, str]]
        """
        if not pre_answer:
            pre_answer = ("class:instruction", " ")
        if not post_answer:
            post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> str:
        """Display the filepath prompt and returns the result.

        :return: user entered filepath
        :rtype: str
        """
        return self.session.prompt(default=self.default)
