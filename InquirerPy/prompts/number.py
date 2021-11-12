"""Module contains the class to create a number prompt."""
from typing import Any, Callable, Union, cast

from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.layout.containers import (
    Float,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension

from InquirerPy.base.complex import BaseComplexPrompt
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

__all__ = ["NumberPrompt"]


class NumberPrompt(BaseComplexPrompt):
    """Create a input prompts that only takes number as input."""

    def __init__(
        self,
        message: InquirerPyMessage,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        default: InquirerPyDefault = "",
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
            instruction=instruction,
            long_instruction=long_instruction,
            validate=validate,
            invalid_message=invalid_message,
            transformer=transformer,
            filter=filter,
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

        self._layout = FloatContainer(
            content=HSplit(
                [
                    VSplit(
                        [
                            Window(
                                height=LayoutDimension.exact(1)
                                if not self._wrap_lines
                                else None,
                                content=FormattedTextControl(self._message),
                                wrap_lines=self._wrap_lines,
                                dont_extend_height=True,
                            )
                        ]
                    )
                ]
            ),
            floats=[
                Float(
                    content=ValidationWindow(
                        invalid_message=self._invalid_message,
                        filter=self._is_invalid & ~IsDone(),
                        wrap_lines=self._wrap_lines,
                    ),
                    left=0,
                    bottom=self._validation_window_bottom_offset,
                )
            ],
        )

    def _handle_down(self) -> None:
        pass

    def _handle_up(self) -> None:
        pass

    def _handle_left(self) -> None:
        pass

    def _handle_right(self) -> None:
        pass
