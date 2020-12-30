"""Module contains the main question function to create a confirm prompt."""
from typing import Any, Callable, Dict, List, Tuple

from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgument


class ConfirmPrompt(BaseSimplePrompt):
    """A wrapper class around PromptSession.

    This class is used for confirm prompt.

    :param message: the question message to display
    :type message: str
    :param style: the style dictionary to apply
    :type style: Dict[str, str]
    :param default: set default answer to true
    :type default: bool
    :param qmark: the custom qmark to display infront of the question
    :type qmark: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[str], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = None,
        default: bool = False,
        qmark: str = "?",
        transformer: Callable[[str], Any] = None,
        filter: Callable[[Any], Any] = None,
        **kwargs
    ) -> None:
        """Construct a PromptSession object and apply keybindings."""
        super().__init__(
            message=message,
            style=style,
            editing_mode="default",
            qmark=qmark,
            transformer=transformer,
            filter=filter,
        )
        self._default = default
        if not isinstance(self._default, bool):
            raise InvalidArgument(
                "default for confirm type question should be type of bool."
            )

        @self._kb.add("y")
        @self._kb.add("Y")
        def _(event) -> None:
            """Bind y and Y to accept confirmation."""
            self._session.default_buffer.text = ""
            self.status["answered"] = True
            self.status["result"] = True
            event.app.exit(result=True)

        @self._kb.add("n")
        @self._kb.add("N")
        def _(event) -> None:
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
        def _(event) -> None:
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

        :return: a list of formatted message to use for PromptSession
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = (
            "class:instruction",
            "%s" % " (Y/n)" if self._default else " (y/N)",
        )
        post_answer = ("class:answer", " Yes" if self.status["result"] else " No")
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> bool:
        """Display a confirm prompt and get user input for confirmation.

        :return: user selected answer, either True or False
        :rtype: bool
        """
        result = self._session.prompt()
        if not self._filter:
            return result
        return self._filter(result)
