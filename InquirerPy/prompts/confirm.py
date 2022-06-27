"""Module contains the class to create a confirm prompt."""
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from prompt_toolkit.buffer import ValidationState
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.validation import ValidationError

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
)

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.key_binding.key_processor import KeyPressEvent
    from prompt_toolkit.output.base import Output

__all__ = ["ConfirmPrompt"]


class ConfirmPrompt(BaseSimplePrompt):
    """Create a prompt that provides 2 options (confirm/deny) and controlled via single keypress.

    A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Used for compatibility .
        default: Set the default value of the prompt, should be either `True` or `False`.
            This affects the value returned when user directly hit `enter` key.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the question.
        long_instruction: Long instructions to display at the bottom of the prompt.
        transformer: A function which performs additional transformation on the value that gets printed to the terminal.
            Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:transformer` documentation for more details.
        filter: A function which performs additional transformation on the result.
            This affects the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:filter` documentation for more details.
        keybindings: Customise the builtin keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more details.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        confirm_letter: Letter used to confirm the prompt. A keybinding will be created for this letter.
            Default is `y` and pressing `y` will answer the prompt with value `True`.
        reject_letter: Letter used to reject the prompt. A keybinding will be created for this letter.
            Default is `n` and pressing `n` will answer the prompt with value `False`.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.
        input: Used internally and will be removed in future updates.
        output: Used internally and will be removed in future updates.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.confirm(message="Confirm?").execute()
        >>> print(result)
        True
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        default: InquirerPyDefault = False,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        transformer: Optional[Callable[[bool], Any]] = None,
        filter: Optional[Callable[[bool], Any]] = None,
        keybindings: Optional[InquirerPyKeybindings] = None,
        wrap_lines: bool = True,
        confirm_letter: str = "y",
        reject_letter: str = "n",
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
        input: Optional["Input"] = None,
        output: Optional["Output"] = None,
    ) -> None:
        vi_mode = False
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            transformer=transformer,
            filter=filter,
            default=default,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
        )
        if not isinstance(self._default, bool):
            raise InvalidArgument(
                f"{type(self).__name__} argument default should be type of bool"
            )
        self._confirm_letter = confirm_letter
        self._reject_letter = reject_letter

        if not keybindings:
            keybindings = {}
        self.kb_maps = {
            "confirm": [
                {"key": self._confirm_letter},
                {"key": self._confirm_letter.upper()},
            ],
            "reject": [
                {"key": self._reject_letter},
                {"key": self._reject_letter.upper()},
            ],
            "any": [{"key": Keys.Any}],
            **keybindings,
        }
        self.kb_func_lookup = {
            "confirm": [{"func": self._handle_confirm}],
            "reject": [{"func": self._handle_reject}],
            "any": [{"func": lambda _: None}],
        }
        self._keybinding_factory()

        self._session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self._kb,
            style=self._style,
            wrap_lines=self._wrap_lines,
            bottom_toolbar=[("class:long_instruction", long_instruction)]
            if long_instruction
            else None,
            input=input,
            output=output,
        )

    def _set_error(self, message: str) -> None:
        self._session.default_buffer.validation_state = ValidationState.INVALID
        self._session.default_buffer.validation_error = ValidationError(message=message)

    def _handle_reject(self, event) -> None:
        self._session.default_buffer.text = ""
        self.status["answered"] = True
        self.status["result"] = False
        event.app.exit(result=False)

    def _handle_confirm(self, event) -> None:
        self._session.default_buffer.text = ""
        self.status["answered"] = True
        self.status["result"] = True
        event.app.exit(result=True)

    def _handle_enter(self, event: "KeyPressEvent") -> None:
        self.status["answered"] = True
        self.status["result"] = self._default
        event.app.exit(result=self._default)

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get message to display infront of the input buffer.

        Returns:
            Formatted text in list of tuple format.
        """
        if not self.instruction:
            pre_answer = (
                "class:instruction",
                " (%s/%s) " % (self._confirm_letter.upper(), self._reject_letter)
                if self._default
                else " (%s/%s) " % (self._confirm_letter, self._reject_letter.upper()),
            )
        else:
            pre_answer = ("class:instruction", " %s " % self.instruction)
        post_answer = ("class:answer", " Yes" if self.status["result"] else " No")
        return super()._get_prompt_message(pre_answer, post_answer)

    def _run(self) -> bool:
        return self._session.prompt()

    async def _run_async(self) -> Any:
        return await self._session.prompt_async()
