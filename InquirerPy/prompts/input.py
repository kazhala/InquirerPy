"""Module contains the class to create an input prompt."""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion.base import Completer
from prompt_toolkit.filters.base import Condition
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.shortcuts.prompt import CompleteStyle, PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["InputPrompt"]


class InputPrompt(BaseSimplePrompt):
    """A wrapper class around PromptSession.

    This class is used for input prompt.

    :param message: The question to ask.
    :param style: A dictionary of style to apply.
    :param vi_mode: Use vi kb for the prompt.
    :param default: The default result.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param instruction: Instruction to display after the question message.
    :param completer: Add auto completer to user input.
    :param multicolumn_complete: Complete in multi column.
    :param multiline: Enable multiline mode.
    :param validate: A callable or a validation class to validate user input.
    :param invalid_message: The error message to display when input is invalid.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        default: Union[str, Callable[[SessionResult], str]] = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        completer: Union[Dict[str, Optional[str]], Completer] = None,
        multicolumn_complete: bool = False,
        multiline: bool = False,
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[str], Any] = None,
        filter: Callable[[str], Any] = None,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
        **kwargs,
    ) -> None:
        super().__init__(
            message,
            style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            validate=validate,
            invalid_message=invalid_message,
            transformer=transformer,
            filter=filter,
            session_result=session_result,
            default=default,
            wrap_lines=wrap_lines,
        )
        if not isinstance(self._default, str):
            raise InvalidArgument(
                "default for input type question should be type of str."
            )
        self._completer = None
        if isinstance(completer, dict):
            self._completer = NestedCompleter.from_nested_dict(completer)
        elif isinstance(completer, Completer):
            self._completer = completer
        self._multiline = multiline
        self._complete_style = (
            CompleteStyle.COLUMN
            if not multicolumn_complete
            else CompleteStyle.MULTI_COLUMN
        )

        @Condition
        def is_multiline():
            return self._multiline

        @Condition
        def has_completion():
            return self._completer is not None

        @self._kb.add("c-space", filter=has_completion)
        def completion(event):
            buff = event.app.current_buffer
            if buff.complete_state:
                buff.complete_next()
            else:
                buff.start_completion(select_first=False)

        @self._kb.add(Keys.Enter, filter=~is_multiline)
        def enter(event):
            try:
                self._session.validator.validate(self._session.default_buffer)  # type: ignore
            except ValidationError:
                self._session.default_buffer.validate_and_handle()
            else:
                self.status["answered"] = True
                self.status["result"] = self._session.default_buffer.text
                self._session.default_buffer.text = ""
                event.app.exit(result=self.status["result"])

        @self._kb.add(Keys.Escape, Keys.Enter, filter=is_multiline)
        def multiline_enter(event):
            try:
                self._session.validator.validate(self._session.default_buffer)  # type: ignore
            except ValidationError:
                self._session.default_buffer.validate_and_handle()
            else:
                self.status["answered"] = True
                self.status["result"] = self._session.default_buffer.text
                self._session.default_buffer.text = ""
                event.app.exit(result=self.status["result"])

        self._session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self._kb,
            style=self._style,
            completer=self._completer,
            validator=self._validator,
            validate_while_typing=False,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
            editing_mode=self._editing_mode,
            lexer=SimpleLexer(self._lexer),
            is_password=kwargs.pop("is_password", False),
            multiline=self._multiline,
            complete_style=self._complete_style,
            wrap_lines=wrap_lines,
        )

    def _get_prompt_message(
        self,
        pre_answer: Optional[Tuple[str, str]] = None,
        post_answer: Optional[Tuple[str, str]] = None,
    ) -> List[Tuple[str, str]]:
        """Dynamically update the prompt message.

        Change the user input path to the 'answer' color in style.

        :param pre_answer: The formatted text to display before answering the question.
        :param post_answer: The formatted text to display after answering the question.
        :return: The formatted text for PromptSession.
        """
        if not pre_answer:
            if self._multiline and not self._instruction:
                pre_answer = ("class:instruction", " ESC + Enter to finish input")
            else:
                pre_answer = (
                    "class:instruction",
                    " %s " % self.instruction if self.instruction else " ",
                )
        if not post_answer:
            if self._multiline and self.status["result"]:
                lines = self.status["result"].split("\n")
                if len(lines) > 1:
                    number_of_chars = len("".join(lines[1:]))
                    lines[0] += "...[%s char%s]" % (
                        number_of_chars,
                        "s" if number_of_chars > 1 else "",
                    )
                post_answer = ("class:answer", " %s" % lines[0])
            else:
                post_answer = ("class:answer", " %s" % self.status["result"])

        formatted_message = super()._get_prompt_message(pre_answer, post_answer)
        if not self.status["answered"] and self._multiline:
            formatted_message.append(
                ("class:questionmark", "\n%s " % INQUIRERPY_POINTER_SEQUENCE)
            )
        return formatted_message

    def _run(self) -> str:
        return self._session.prompt(default=self._default)
