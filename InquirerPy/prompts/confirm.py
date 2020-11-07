"""Module contains the main question function to create a confirm prompt."""
from typing import Any, Dict, List, Tuple, TypeVar, Union

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.styles import Style


def question(
    message: str, style: Dict[str, str], default_true: bool = False, symbol: str = "?"
) -> bool:
    """Display a confirm prompt and get user input for confirmation.

    :param message: the question message to display
    :type message: str
    :param style: the style dictionary to apply
    :type style: Dict[str, str]
    :param default_true: set default answer to true
    :type default_true: bool
    :param symbol: the custom symbol to display infront of the question
    :type symbol: str
    :return: user selected answer
    :rtype: bool
    """
    question_style = Style.from_dict(style)
    status = {"answered": False, "result": None}

    kb = KeyBindings()

    @kb.add("c-c")
    def _(event) -> None:
        """Raise KeyboardInterrupt when ctrl-c is pressed.

        Remove the extra empty line raised by prompt_toolkit by default.
        """
        raise KeyboardInterrupt

    @kb.add("y")
    @kb.add("Y")
    def _(event) -> None:
        """Bind y and Y to accept confirmation."""
        session.default_buffer.text = ""
        status["answered"] = True
        status["result"] = True
        event.app.exit(result=True)

    @kb.add("n")
    @kb.add("N")
    def _(event) -> None:
        """Bind n and N to reject confirmation."""
        session.default_buffer.text = ""
        status["answered"] = True
        status["result"] = False
        event.app.exit(result=False)

    @kb.add(Keys.Any)
    def _(event) -> None:
        """Disable all other key presses."""
        pass

    @kb.add(Keys.Enter)
    def _(event) -> None:
        """Bind enter to use the default answer."""
        status["answered"] = True
        status["result"] = default_true
        event.app.exit(result=default_true)

    def get_prompt_message() -> List[Tuple[str, str]]:
        """Dynamically update the prompt message.

        After user select an answer, remove (Y/n) or (y/N) and inject
        the pretty answer.

        :return: a list of formatted message to use for PromptSession
        :rtype: List[Tuple[str, str]]
        """
        display_message = []
        display_message.append(("class:symbol", symbol))
        display_message.append(("class:question", " %s " % message))
        if status["answered"]:
            display_message.append(
                ("class:answer", " Yes" if status["result"] else " No")
            )
        else:
            display_message.append(
                ("class:instruction", " %s" % " (Y/n)" if default_true else " (y/N)")
            )
        return display_message

    session = PromptSession(
        message=get_prompt_message,
        key_bindings=kb,
        mouse_support=False,
        style=question_style,
        erase_when_done=False,
    )

    return session.prompt()
