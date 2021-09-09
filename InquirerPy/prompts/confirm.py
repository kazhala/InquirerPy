"""Module contains the class to create a confirm prompt."""
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Union

from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import InquirerPyStyle, SessionResult

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.output.base import Output


__all__ = ["ConfirmPrompt"]


class ConfirmPrompt(BaseSimplePrompt):
    """A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Create a prompt that provide 2 options (confirm/deny).

    Args:
        message: The question to ask the user.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        default: The default value when user hit `enter`. A boolean value of either `True` or `False`.
        vi_mode: Used for compatibility, ignore this parameter.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the `message`.
        transformer: A callable to transform the result that gets printed in the terminal.
            This is visual effect only.
        filter: A callable to filter the result that gets returned.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        confirm_letter: Letter used to confirm the prompt. A keybinding will be created for this letter.
        reject_letter: Letter used to reject the prompt. A keybinding will be created for this letter.
        session_result: Used for `classic syntax`, ignore this parameter.
        input: Used for testing, ignore this parameter.
        output: Used for testing, ignore this parameter.

    Examples:
        >>> result = ConfirmPrompt(message="Confirm?").execute()
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        default: Union[bool, Callable[[Dict[str, Any]], bool]] = False,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        transformer: Callable[[bool], Any] = None,
        filter: Callable[[bool], Any] = None,
        wrap_lines: bool = True,
        confirm_letter: str = "y",
        reject_letter: str = "n",
        session_result: SessionResult = None,
        input: "Input" = None,
        output: "Output" = None,
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
            session_result=session_result,
        )
        if not isinstance(self._default, bool):
            raise InvalidArgument(
                "confirm prompt argument default should be type of bool"
            )
        self._confirm_letter = confirm_letter
        self._reject_letter = reject_letter

        @self._kb.add(self._confirm_letter)
        @self._kb.add(self._confirm_letter.upper())
        def confirm(event) -> None:
            self._session.default_buffer.text = ""
            self.status["answered"] = True
            self.status["result"] = True
            event.app.exit(result=True)

        @self._kb.add(self._reject_letter)
        @self._kb.add(self._reject_letter.upper())
        def reject(event) -> None:
            self._session.default_buffer.text = ""
            self.status["answered"] = True
            self.status["result"] = False
            event.app.exit(result=False)

        @self._kb.add(Keys.Any)
        def _(event) -> None:
            """Disable all other key presses."""
            pass

        @self._kb.add(Keys.Enter)
        def enter(event) -> None:
            self.status["answered"] = True
            self.status["result"] = self._default
            event.app.exit(result=self._default)

        self._session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self._kb,
            style=self._style,
            wrap_lines=self._wrap_lines,
            input=input,
            output=output,
        )

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
