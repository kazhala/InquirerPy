"""Module contains the class to create an input prompt."""
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

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

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.output.base import Output

__all__ = ["InputPrompt"]


class InputPrompt(BaseSimplePrompt):
    """A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Create a text prompt that accepts user input.

    Args:
        message: The question to ask the user.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        vi_mode: Use vim keybinding for the prompt.
        default: The default text value to add to the input.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the `message`.
        completer: Auto completer to add to the input prompt.
        multicolumn_complete: Complete in multi column.
        multiline: Enable multiline mode.
        validate: Validation callable or class to validate user input.
        invalid_message: Error message to display when input is invalid.
        transformer: A callable to transform the result that gets printed in the terminal.
            This is visual effect only.
        filter: A callable to filter the result that gets returned.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        is_password: Used by :class:`~InquirerPy.prompts.secret.SecretPrompt`, ignore this parameter.
        session_result: Used for `classic syntax`, ignore this parameter.
        input: Used for testing, ignore this parameter.
        output: Used for testing, ignore this parameter.

    Examples:
        >>> result = InputPrompt(message="Enter your name:").execute()
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
        is_password: bool = False,
        session_result: SessionResult = None,
        input: "Input" = None,
        output: "Output" = None,
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
            raise InvalidArgument("input prompt argument default should be type of str")
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
            input=input,
            output=output,
            editing_mode=self._editing_mode,
            lexer=SimpleLexer(self._lexer),
            is_password=is_password,
            multiline=self._multiline,
            complete_style=self._complete_style,
            wrap_lines=wrap_lines,
        )

    def _get_prompt_message(
        self,
        pre_answer: Optional[Tuple[str, str]] = None,
        post_answer: Optional[Tuple[str, str]] = None,
    ) -> List[Tuple[str, str]]:
        """Get message to display infront of the input buffer.

        Args:
            pre_answer: The formatted text to display before answering the question.
            post_answer: The formatted text to display after answering the question.

        Returns:
            Formatted text in list of tuple format.
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
