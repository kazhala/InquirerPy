"""Contains the base class :class:`.BaseSimplePrompt`."""
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Union, cast

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyBindings, KeyHandlerCallable
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles.style import Style
from prompt_toolkit.validation import Validator

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.utils import InquirerPyStyle, SessionResult, get_style


class BaseSimplePrompt(ABC):
    """The base class to create a simple terminal input prompt.

    Note:
        No actual :class:`~prompt_toolkit.application.Application` is created by this class.
        This class only creates some common interface and attributes that can be easily used
        by `prompt_toolkit`.

        To have a functional prompt, you'll at least have to implement the :meth:`.BaseSimplePrompt._run`
        and :meth:`.BaseSimplePrompt._get_prompt_message`.

    See Also:
        :class:`~InquirerPy.prompts.input.InputPrompt`
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
        self._result = session_result or {}
        self._message = (
            message
            if not isinstance(message, Callable)
            else cast(Callable, message)(self._result)
        )
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
        """Dict[str, Any]: Get current prompt status.

        The status contains 2 keys: "answered" and "result".

        `answered`: If the current prompt is answered.

        `result`: The result of the user answer.
        """
        return self._status

    @status.setter
    def status(self, value) -> None:
        self._status = value

    def register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True, **kwargs
    ) -> Callable[[KeyHandlerCallable], KeyHandlerCallable]:
        """Keybinding registration decorator.

        This decorator wraps around the :meth:`prompt_toolkit.key_binding.KeyBindings.add` with
        added feature to process `alt` realted keybindings.

        By default, `prompt_toolkit` doesn't process `alt` related keybindings,
        it requires `alt-ANY` to `escape` + `ANY`.

        Args:
            keys: The keys to bind that can trigger the function.
            filter: :class:`~prompt_toolkit.filter.Condition` to indicate if this keybinding should be active.

        Returns:
            A decorator that should be applied to the function thats intended to be active when the keys
            are pressed.

        Examples:
            >>> @self.register_kb("alt-j")
            ... def test(event):
            ...     pass
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

            @self._kb.add(*formatted_keys, filter=filter, **kwargs)
            def executable(event) -> None:
                func(event)

            return executable

        return decorator

    @abstractmethod
    def _get_prompt_message(
        self, pre_answer: Tuple[str, str], post_answer: Tuple[str, str]
    ) -> List[Tuple[str, str]]:
        """Get the question message in formatted text form to display in the prompt.

        This function is mainly used to render the question message dynamically based
        on the current status (answered or not answered) of the prompt.

        Note:
            The function requires implementation when inheriting :class:`.BaseSimplePrompt`.
            You should call `super()._get_prompt_message(pre_answer, post_answer)` in
            the implemented `_get_prompt_message`.

        Args:
            pre_answer: The message to display before the question is answered.
            post_answer: The information to display after the question is answered.

        Returns:
            Formatted text in list of tuple format.
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
        """Abstractmethod to enforce a run function is implemented.

        All prompt instance require a `_run` call to initialise and run an instance of
        `PromptSession` or `Application`.
        """
        pass

    def execute(self, raise_keyboard_interrupt: bool = True) -> Any:
        """Run the prompt and get the result.

        Args:
            raise_keyboard_interrupt: **Deprecated**. Set this parameter on the prompt initialisation instead.

        Returns:
            Value of the user answer. Types varies depending on the prompt.

        Raises:
            KeyboardInterrupt: When `ctrl-c` is pressed and `raise_keyboard_interrupt` is True.
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
        """str: Instruction to display next to question."""
        return self._instruction
