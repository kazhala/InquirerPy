"""Contains the interface class :class:`.BaseComplexPrompt` for more complex prompts and the mocked document class :class:`.FakeDocument`."""
import asyncio
import shutil
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from prompt_toolkit.application import Application
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import Condition, FilterOrBool
from prompt_toolkit.key_binding.key_bindings import KeyHandlerCallable
from prompt_toolkit.keys import Keys
from prompt_toolkit.validation import Validator

from InquirerPy.base.simple import BaseSimplePrompt
from InquirerPy.containers import SpinnerWindow
from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.utils import InquirerPySessionResult, InquirerPyStyle


@dataclass
class FakeDocument:
    """A fake `prompt_toolkit` document class.

    Work around to allow non-buffer type :class:`~prompt_toolkit.layout.UIControl` to use
    :class:`~prompt_toolkit.validation.Validator`.

    Args:
        text: Content to be validated.
        cursor_position: Fake cursor position.
    """

    text: str
    cursor_position: int = 0


class BaseComplexPrompt(BaseSimplePrompt):
    """A base class to create a more complex prompt that will involve :class:`~prompt_toolkit.application.Application`.

    Note:
        This class does not create :class:`~prompt_toolkit.layout.Layout` nor :class:`~prompt_toolkit.application.Application`,
        it only contains the necessary attributes and helper functions to be consumed.

    Note:
        Use :class:`~InquirerPy.base.BaseListPrompt` to create a complex list prompt which involves multiple choices. It has
        more methods and helper function implemented.

    See Also:
        :class:`~InquirerPy.base.BaseListPrompt`
        :class:`~InquirerPy.prompts.fuzzy.FuzzyPrompt`
    """

    def __init__(
        self,
        message: Union[str, Callable[[InquirerPySessionResult], str]],
        style: InquirerPyStyle = None,
        border: bool = False,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        wrap_lines: bool = True,
        spinner_enable: bool = False,
        spinner_pattern: List[str] = None,
        spinner_text: str = "",
        spinner_delay: float = 0.1,
        set_exception_handler: bool = True,
        session_result: InquirerPySessionResult = None,
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            wrap_lines=wrap_lines,
            session_result=session_result,
        )
        self._invalid_message = invalid_message
        self._rendered = False
        self._invalid = False
        self._loading = False
        self._application: Application
        self._spinner_enable = spinner_enable
        self._set_exception_handler = set_exception_handler
        self._long_instruction = long_instruction
        self._border = border
        self._height_offset = 2  # prev prompt result + current prompt question
        if self._border:
            self._height_offset += 2
        if self._long_instruction:
            self._height_offset += 1

        self._is_vim_edit = Condition(lambda: self._editing_mode == EditingMode.VI)
        self._is_invalid = Condition(lambda: self._invalid)
        self._is_loading = Condition(lambda: self.loading)
        self._is_spinner_enable = Condition(lambda: self._spinner_enable)
        self._is_displaying_long_instruction = Condition(
            lambda: self._long_instruction != ""
        )

        self._spinner = SpinnerWindow(
            loading=self._is_loading & self._is_spinner_enable,
            redraw=self._redraw,
            pattern=spinner_pattern,
            text=spinner_text or cast(str, self._message),
            delay=spinner_delay,
        )

        @self._register_kb("enter")
        def _(event):
            self._handle_enter(event)

    def _redraw(self) -> None:
        """Redraw the application UI."""
        self._application.invalidate()

    def _register_kb(
        self, *keys: Union[Keys, str], filter: FilterOrBool = True
    ) -> Callable[[KeyHandlerCallable], KeyHandlerCallable]:
        """Decorate keybinding registration function.

        Ensure that the `invalid` state is cleared on next keybinding entered.
        """

        def decorator(func: KeyHandlerCallable) -> KeyHandlerCallable:
            @self.register_kb(*keys, filter=filter)
            def executable(event):
                if self._invalid:
                    self._invalid = False
                func(event)

            return executable

        return decorator

    def _exception_handler(self, _, context) -> None:
        """Set exception handler for the event loop.

        Skip the question and raise exception.

        Args:
            loop: Current event loop.
            context: Exception context.
        """
        self._status["answered"] = True
        self._status["result"] = INQUIRERPY_KEYBOARD_INTERRUPT
        self._application.exit(exception=context["exception"])

    def _after_render(self, app: Optional[Application]) -> None:
        """Run after the :class:`~prompt_toolkit.application.Application` is rendered/updated.

        Since this function is fired up on each render, adding a check on `self._rendered` to
        process logics that should only run once.

        Set event loop exception handler here, since its guaranteed that the event loop is running
        in `_after_render`.
        """
        if not self._rendered:
            self._rendered = True

            try:
                if self._set_exception_handler:
                    loop = asyncio.get_running_loop()
                    loop.set_exception_handler(self._exception_handler)
            except RuntimeError:
                pass

            def keybinding_factory(keys, filter, action):
                if not isinstance(keys, list):
                    keys = [keys]

                @self._register_kb(*keys, filter=filter)
                def _(_):
                    for method in self.kb_func_lookup[action]:
                        method["func"](*method.get("args", []))

            for key, item in self.kb_maps.items():
                for kb in item:
                    keybinding_factory(
                        kb["key"], kb.get("filter", Condition(lambda: True)), key
                    )

            self._on_rendered(app)

    def _set_error(self, message: str) -> None:
        """Set error message and set invalid state.

        Args:
            message: Error message to display.
        """
        self._invalid_message = message
        self._invalid = True

    def _get_error_message(self) -> List[Tuple[str, str]]:
        """Obtain the error message dynamically.

        Returns:
            FormattedText in list of tuple format.
        """
        return [
            (
                "class:validation-toolbar",
                self._invalid_message,
            )
        ]

    def _on_rendered(self, _: Optional[Application]) -> None:
        """Run once after the UI is rendered. Acts like `ComponentDidMount`."""
        pass

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get the prompt message to display.

        Returns:
            Formatted text in list of tuple format.
        """
        pre_answer = (
            "class:instruction",
            " %s " % self.instruction if self.instruction else " ",
        )
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def _run(self) -> Any:
        """Run the application."""
        return self.application.run()

    @property
    def application(self) -> Application:
        """Get the application.

        :class:`.BaseComplexPrompt` requires :attr:`.BaseComplexPrompt._application` to be defined since this class
        doesn't implement :class:`~prompt_toolkit.layout.Layout` and :class:`~prompt_toolkit.application.Application`.

        Raises:
            NotImplementedError: When `self._application` is not defined.
        """
        if not self._application:
            raise NotImplementedError
        return self._application

    @application.setter
    def application(self, value: Application) -> None:
        self._application = value

    @abstractmethod
    def _handle_enter(self, event) -> None:
        """Handle event when user input enter key.

        Make sure to use the :class:`.FakeDocument` class to validate
        the user choice in the function implmentation.
        """
        pass

    @property
    def height_offset(self) -> int:
        """int: Height offset to apply."""
        if not self._wrap_lines:
            return self._height_offset
        return self.extra_lines_due_to_wrapping + self._height_offset

    @property
    def total_message_length(self) -> int:
        """int: Total length of the message."""
        total_message_length = 0
        if self._qmark:
            total_message_length += len(self._qmark)
            total_message_length += 1  # Extra space if qmark is present
        total_message_length += len(str(self._message))
        total_message_length += 1  # Extra space between message and instruction
        total_message_length += len(str(self._instruction))
        if self._instruction:
            total_message_length += 1  # Extra space behind the instruction
        return total_message_length

    @property
    def extra_lines_due_to_wrapping(self) -> int:
        """Get the extra lines created caused by line wrapping.

        Used mainly to calculate how much offset should be applied when getting
        the height.

        Returns:
            Total extra lines created due to line wrapping.
        """
        result = 0
        term_width, _ = shutil.get_terminal_size()

        # message wrap
        result += self.total_message_length // term_width
        # long instruction wrap
        result += len(self._long_instruction) // term_width

        return result

    @property
    def loading(self) -> bool:
        """bool: Indicate if the prompt is loading."""
        return self._loading

    @loading.setter
    def loading(self, value: bool) -> None:
        self._loading = value
        if self.loading:
            asyncio.create_task(self._spinner.start())

    @property
    def kb_maps(self) -> Dict[str, Any]:
        """Dict[str, Any]: Keybinding mappings."""
        if not self._kb_maps:
            raise NotImplementedError
        return self._kb_maps

    @kb_maps.setter
    def kb_maps(self, value: Dict[str, Any]) -> None:
        self._kb_maps = value

    @property
    def kb_func_lookup(self) -> Dict[str, Any]:
        """Dict[str, Any]: Keybinding function lookup mappings.."""
        if not self._kb_func_lookup:
            raise NotImplementedError
        return self._kb_func_lookup

    @kb_func_lookup.setter
    def kb_func_lookup(self, value: Dict[str, Any]) -> None:
        self._kb_func_lookup = value
