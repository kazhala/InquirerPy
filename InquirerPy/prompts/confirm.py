"""Module contains the main question function to create a confirm prompt."""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["ConfirmPrompt"]


class ConfirmPrompt(BaseSimplePrompt):
    """A wrapper class around PromptSession.

    This class is used for confirm prompt.

    :param message: The question message to display.
    :param style: The style dictionary to apply.
    :param default: Set default answer value.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: THe custom symbol to display infront of the question after its answered.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        default: Union[bool, Callable[[Dict[str, Any]], bool]] = False,
        qmark: str = "?",
        amark: str = "?",
        transformer: Callable[[bool], Any] = None,
        filter: Callable[[bool], Any] = None,
        session_result: SessionResult = None,
        **kwargs
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            vi_mode=False,
            qmark=qmark,
            amark=amark,
            transformer=transformer,
            filter=filter,
            session_result=session_result,
            default=default,
        )
        if not isinstance(self._default, bool):
            raise InvalidArgument(
                "default for confirm type question should be type of bool."
            )

        @self._kb.add("y")
        @self._kb.add("Y")
        def confirm(event) -> None:
            """Bind y and Y to accept confirmation."""
            self._session.default_buffer.text = ""
            self.status["answered"] = True
            self.status["result"] = True
            event.app.exit(result=True)

        @self._kb.add("n")
        @self._kb.add("N")
        def reject(event) -> None:
            """Bind n and N to reject confirmation."""
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
            """Bind enter to use the default answer."""
            self.status["answered"] = True
            self.status["result"] = self._default
            event.app.exit(result=self._default)

        self._session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self._kb,
            style=self._style,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Dynamically update the prompt message.

        After user select an answer, remove (Y/n) or (y/N) and inject
        the pretty answer.

        :return: A list of formatted message to be consumed by PromptSession.
        """
        pre_answer = (
            "class:instruction",
            "%s" % " (Y/n)" if self._default else " (y/N)",
        )
        post_answer = ("class:answer", " Yes" if self.status["result"] else " No")
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self, raise_keyboard_interrupt: bool = True) -> Optional[bool]:
        """Display a confirm prompt and get user input for confirmation.

        :return: The user selected answer, either True or False.
        """
        result = self._session.prompt()
        if result == INQUIRERPY_KEYBOARD_INTERRUPT:
            if raise_keyboard_interrupt:
                raise KeyboardInterrupt
            else:
                result = None
        if not self._filter:
            return result
        return self._filter(result)
