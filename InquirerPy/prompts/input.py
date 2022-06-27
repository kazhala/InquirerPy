"""Module contains the class to create an input prompt."""
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.buffer import ValidationState
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.completion.base import Completer
from prompt_toolkit.filters.base import Condition
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.shortcuts.prompt import CompleteStyle, PromptSession
from prompt_toolkit.validation import ValidationError

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.key_binding.key_processor import KeyPressEvent
    from prompt_toolkit.output.base import Output

__all__ = ["InputPrompt"]


class InputPrompt(BaseSimplePrompt):
    """Create a text prompt that accepts user input.

    A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default text value of the prompt.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the question.
        long_instruction: Long instructions to display at the bottom of the prompt.
        completer: Add auto completion to the prompt.
            Refer to :ref:`pages/prompts/input:Auto Completion` documentation for more details.
        multicolumn_complete: Change the auto-completion UI to a multi column display.
        multiline: Enable multiline edit. While multiline edit is active, pressing `enter` won't complete the answer.
            and will create a new line. Use `esc` followd by `enter` to complete the question.
        validate: Add validation to user input.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        invalid_message: Error message to display when user input is invalid.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        transformer: A function which performs additional transformation on the value that gets printed to the terminal.
            Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:transformer` documentation for more details.
        filter: A function which performs additional transformation on the result.
            This affects the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:filter` documentation for more details.
        keybindings: Customise the builtin keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more details.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        is_password: Used internally for :class:`~InquirerPy.prompts.secret.SecretPrompt`.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.
        input: Used internally and will be removed in future updates.
        output: Used internally and will be removed in future updates.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.text(message="Enter your name:").execute()
        >>> print(f"Name: {result}")
        Name: Michael
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        default: InquirerPyDefault = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        completer: Optional[Union[Dict[str, Optional[str]], "Completer"]] = None,
        multicolumn_complete: bool = False,
        multiline: bool = False,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        transformer: Optional[Callable[[str], Any]] = None,
        filter: Optional[Callable[[str], Any]] = None,
        keybindings: Optional[InquirerPyKeybindings] = None,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        is_password: bool = False,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
        input: Optional["Input"] = None,
        output: Optional["Output"] = None,
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
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
        )
        if not isinstance(self._default, str):
            raise InvalidArgument(
                f"{type(self).__name__} argument 'default' should be type of str"
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

        if not keybindings:
            keybindings = {}
        self.kb_maps = {
            "answer": [
                {"key": Keys.Enter, "filter": ~is_multiline},
                {"key": [Keys.Escape, Keys.Enter], "filter": is_multiline},
            ],
            "completion": [{"key": "c-space"}],
            **keybindings,
        }
        self.kb_func_lookup = {"completion": [{"func": self._handle_completion}]}
        self._keybinding_factory()

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
            bottom_toolbar=[("class:long_instruction", long_instruction)]
            if long_instruction
            else None,
        )

    def _set_error(self, message: str) -> None:
        self._session.default_buffer.validation_state = ValidationState.INVALID
        self._session.default_buffer.validation_error = ValidationError(message=message)

    def _handle_enter(self, event: "KeyPressEvent") -> None:
        try:
            self._session.validator.validate(self._session.default_buffer)  # type: ignore
        except ValidationError:
            self._session.default_buffer.validate_and_handle()
        else:
            self.status["answered"] = True
            self.status["result"] = self._session.default_buffer.text
            self._session.default_buffer.text = ""
            event.app.exit(result=self.status["result"])

    def _handle_completion(self, event) -> None:
        if self._completer is None:
            return
        buff = event.app.current_buffer
        if buff.complete_state:
            buff.complete_next()
        else:
            buff.start_completion(select_first=False)

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

    async def _run_async(self) -> Any:
        return await self._session.prompt_async(default=self._default)
