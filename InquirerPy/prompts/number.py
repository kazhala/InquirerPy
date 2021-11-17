"""Module contains the class to create a number prompt."""
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    HorizontalAlign,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import (
    BufferControl,
    DummyControl,
    FormattedTextControl,
)
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers.base import SimpleLexer

from InquirerPy.base.complex import BaseComplexPrompt
from InquirerPy.containers.instruction import InstructionWindow
from InquirerPy.containers.validation import ValidationWindow
from InquirerPy.enum import INQUIRERPY_QMARK_SEQUENCE
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
    from prompt_toolkit.key_binding.key_processor import KeyPressEvent

__all__ = ["NumberPrompt"]


class NumberPrompt(BaseComplexPrompt):
    """Create a input prompts that only takes number as input."""

    def __init__(
        self,
        message: InquirerPyMessage,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        default: InquirerPyDefault = 0,
        float_allowed: bool = False,
        max_allowed: Union[int, float] = None,
        min_allowed: Union[int, float] = None,
        qmark: str = INQUIRERPY_QMARK_SEQUENCE,
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        validate: InquirerPyValidate = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[str], Any] = None,
        filter: Callable[[str], Any] = None,
        keybindings: InquirerPyKeybindings = None,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: InquirerPySessionResult = None,
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            instruction=instruction,
            long_instruction=long_instruction,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
        )

        self._float = float_allowed
        self._max = max_allowed
        self._min = min_allowed

        if isinstance(default, Callable):
            default = cast(Callable, default)(session_result)
        if self._float and not isinstance(default, float):
            raise InvalidArgument(
                f"{type(self).__name__} argument 'default' should return type of float"
            )
        elif not isinstance(default, int):
            raise InvalidArgument(
                f"{type(self).__name__} argument 'default' should return type of int"
            )

        if keybindings is None:
            keybindings = {}
        self.kb_maps = {
            "down": [
                {"key": "down"},
                {"key": "c-n", "filter": ~self._is_vim_edit},
                {"key": "j", "filter": self._is_vim_edit},
            ],
            "up": [
                {"key": "up"},
                {"key": "c-p", "filter": ~self._is_vim_edit},
                {"key": "k", "filter": self._is_vim_edit},
            ],
            "left": [{"key": "left"}],
            "right": [{"key": "right"}],
            **keybindings,
        }
        self.kb_func_lookup = {
            "down": [{"func": self._handle_down}],
            "up": [{"func": self._handle_up}],
            "left": [{"func": self._handle_left}],
            "right": [{"func": self._handle_right}],
        }

        self._whole_width = 1
        self._whole_buffer = Buffer(on_text_changed=self._on_whole_text_change)

        self._integral_width = 1
        self._integral_buffer = Buffer(on_text_changed=self._on_integral_text_change)

        self._whole_window = Window(
            height=LayoutDimension.exact(1) if not self._wrap_lines else None,
            content=BufferControl(
                buffer=self._whole_buffer,
                lexer=SimpleLexer("class:input"),
            ),
            width=lambda: Dimension(
                min=self._whole_width,
                max=self._whole_width,
                preferred=self._whole_width,
            ),
            dont_extend_width=True,
        )

        self._integral_window = Window(
            height=LayoutDimension.exact(1) if not self._wrap_lines else None,
            content=BufferControl(
                buffer=self._integral_buffer,
                lexer=SimpleLexer("class:input"),
            ),
            width=lambda: Dimension(
                min=self._integral_width,
                max=self._integral_width,
                preferred=self._integral_width,
            ),
        )

        self._layout = Layout(
            HSplit(
                [
                    VSplit(
                        [
                            Window(
                                height=LayoutDimension.exact(1)
                                if not self._wrap_lines
                                else None,
                                content=FormattedTextControl(self._get_prompt_message),
                                wrap_lines=self._wrap_lines,
                                dont_extend_height=True,
                                dont_extend_width=True,
                            ),
                            self._whole_window,
                            Window(
                                height=LayoutDimension.exact(1)
                                if not self._wrap_lines
                                else None,
                                content=FormattedTextControl([("", ". ")]),
                                wrap_lines=self._wrap_lines,
                                dont_extend_height=True,
                                dont_extend_width=True,
                            ),
                            self._integral_window,
                        ],
                        align=HorizontalAlign.LEFT,
                    ),
                    ConditionalContainer(
                        Window(content=DummyControl()),
                        filter=~IsDone() & self._is_displaying_long_instruction,
                    ),
                    ValidationWindow(
                        invalid_message=self._get_error_message,
                        filter=self._is_invalid & ~IsDone(),
                        wrap_lines=self._wrap_lines,
                    ),
                    InstructionWindow(
                        message=self._long_instruction,
                        filter=~IsDone() & self._is_displaying_long_instruction,
                        wrap_lines=self._wrap_lines,
                    ),
                ]
            ),
        )

        self._layout.focus(self._integral_window)

        self._application = Application(
            layout=self._layout,
            style=self._style,
            key_bindings=self._kb,
            after_render=self._after_render,
        )

    def _on_rendered(self, _) -> None:
        self._whole_buffer.text = "0"
        self._whole_buffer.cursor_position = 1
        self._integral_buffer.text = "0"
        self._integral_buffer.cursor_position = 1

    def _handle_down(self, event: Optional["KeyPressEvent"]) -> None:
        pass

    def _handle_up(self, event: Optional["KeyPressEvent"]) -> None:
        pass

    def _handle_left(self, event: Optional["KeyPressEvent"]) -> None:
        pass

    def _handle_right(self, event: Optional["KeyPressEvent"]) -> None:
        pass

    def _handle_enter(self, event: Optional["KeyPressEvent"]) -> None:
        pass

    def _on_whole_text_change(self, buffer: Buffer) -> None:
        self._whole_width = len(buffer.text) + 1

    def _on_integral_text_change(self, buffer: Buffer) -> None:
        self._integral_width = len(buffer.text) + 1
