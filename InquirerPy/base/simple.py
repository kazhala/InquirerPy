"""Contains the base class `BaseSimplePrompt` for all types of prompts."""
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Union

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyBindings, KeyHandlerCallable
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import Validator

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.utils import InquirerPyStyle, SessionResult, get_style


class BaseSimplePrompt(ABC):
    """The base class for simple prompts.

    Inherit this class to create a simple prompt that leverage `prompt_toolkit`
    PromptSession.

    Note: the PromptSession is not initialised in the constructor, require
    a call of `self.session = PromptSession(...)`.

    :param message: The question message to display.
    :param style: The style dictionary to apply.
    :param vi_mode: Use vi kb for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param instruction: Instruction to display after the question message.
    :param validate: A callable or Validator instance to validate user input.
    :param invalid_message: The message to display when input is invalid.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param session_result: The current session result, this is used by callable message and choices
        to generate dynamic values. If using alternate syntax, skip this value.
    :param default: Default value for the prompt.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        default: Any = "",
        wrap_lines: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Construct the base class for simple prompts."""
        self._result = session_result or {}
        self._message = message if not isinstance(message, Callable) else message(self._result)  # type: ignore
        self._instruction = instruction
        self._default = (
            default if not isinstance(default, Callable) else default(self._result)
        )
        self._style = Style.from_dict(style.dict if style else get_style().dict)
        self._qmark = qmark
        self._amark = amark
        self._status = {"answered": False, "result": None}
        self._kb = KeyBindings()
        self._lexer = "class:input"
        self._transformer = transformer
        self._filter = filter
        self._wrap_lines = wrap_lines
        self._editing_mode = (
            EditingMode.VI
            if vi_mode or bool(os.getenv("INQUIRERPY_VI_MODE", False))
            else EditingMode.EMACS
        )
        if isinstance(validate, Validator):
            self._validator = validate
        else:
            self._validator = Validator.from_callable(
                validate if validate else lambda _: True,
                invalid_message,
                move_cursor_to_end=True,
            )

        @self._kb.add("c-c")
        def _(event) -> None:
            self.status["answered"] = True
            self.status["result"] = INQUIRERPY_KEYBOARD_INTERRUPT
            event.app.exit(result=INQUIRERPY_KEYBOARD_INTERRUPT)

    @property
    def status(self) -> Dict[str, Any]:
        """Get status value of the prompt."""
        return self._status

    @status.setter
    def status(self, value) -> None:
        """Set status value of the prompt."""
        self._status = value

    def register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True
    ) -> Callable[[KeyHandlerCallable], KeyHandlerCallable]:
        """Decorate keybinding registration function.

        Format all alt related keybindings.

        Due to `prompt_toolkit` doesn't process alt related keybindings,
        it requires alt-ANY to "escape" + "ANY".

        Check a list of keys argument if they are alt related, change
        them to escape.

        :param keys: The keys to bind into the keybindings
        :param filter: Condition of whether this keybinding should be active.
        :return: A decorator that should be applied to the function thats intended
            to be active when the keys being pressed.
        """
        alt_pattern = re.compile(r"^alt-(.*)")

        def decorator(func: KeyHandlerCallable) -> KeyHandlerCallable:
            formatted_keys = []
            for key in keys:
                match = alt_pattern.match(key)
                if match:
                    formatted_keys.append("escape")
                    formatted_keys.append(match.group(1))
                else:
                    formatted_keys.append(key)

            @self._kb.add(*formatted_keys, filter=filter)
            def executable(event) -> None:
                func(event)

            return executable

        return decorator

    @abstractmethod
    def _get_prompt_message(
        self, pre_answer: Tuple[str, str], post_answer: Tuple[str, str]
    ) -> List[Tuple[str, str]]:
        """Return the formatted text to display in the prompt.

        Leveraging the nature of Dict in python, we can dynamically update the prompt
        message of the PromptSession.

        This is useful to format/customize user input for better visual.

        :param pre_answer: The information to display before answering the question.
        :param post_answer: The information to display after answering the question.
        :return: Formatted text thats ready to be consumed by PromptSession.
        """
        display_message = []
        if self.status["result"] == INQUIRERPY_KEYBOARD_INTERRUPT:
            display_message.append(("class:skipped", self._qmark))
            display_message.append(
                ("class:skipped", "%s%s " % (" " if self._qmark else "", self._message))
            )
        else:
            if self.status["answered"]:
                display_message.append(("class:answermark", self._amark))
                display_message.append(
                    (
                        "class:answered_question",
                        "%s%s" % (" " if self._amark else "", self._message),
                    )
                )
                display_message.append(
                    post_answer
                    if not self._transformer
                    else (
                        "class:answer",
                        " %s" % self._transformer(self.status["result"]),
                    )
                )
            else:
                display_message.append(("class:questionmark", self._qmark))
                display_message.append(
                    (
                        "class:question",
                        "%s%s" % (" " if self._qmark else "", self._message),
                    )
                )
                display_message.append(pre_answer)
        return display_message

    @abstractmethod
    def _run(self) -> Any:
        """Abstractmethod to enforce a run function is implemented for eaiser management.

        All prompt instance require a run call to initialised the `PromptSession` or `Application`.
        """
        pass

    def execute(self, raise_keyboard_interrupt: bool = True) -> Any:
        """Run the prompt and get the result.

        :param raise_keyboard_interrupt: Raise kbi exception when user hit 'c-c'.
        :return: User entered/selected value.
        """
        result = self._run()
        if result == INQUIRERPY_KEYBOARD_INTERRUPT:
            if raise_keyboard_interrupt and not os.getenv(
                "INQUIRERPY_NO_RAISE_KBI", False
            ):
                raise KeyboardInterrupt
            else:
                result = None
        if not self._filter:
            return result
        return self._filter(result)

    @property
    def instruction(self) -> str:
        """Instruction to display next to question.

        :return: Instruction text
        """
        return self._instruction
