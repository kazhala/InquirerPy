"""Module contains spinner related resources.

Note:
    The spinner is not a standalone spinner to run in the terminal
    but rather a `prompt_toolkit` :class:`~prompt_toolkit.layout.Window` that displays a spinner.

    Use library such as `yaspin <https://github.com/pavdmyt/yaspin>`_ if you need a plain spinner.
"""
import asyncio
from typing import TYPE_CHECKING, Callable, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit.filters.utils import to_filter
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl

if TYPE_CHECKING:
    from prompt_toolkit.filters.base import Filter

__all__ = ["SPINNERS", "SpinnerWindow"]


class SPINNERS(NamedTuple):
    """Presets of spinner patterns.

    See Also:
        https://github.com/pavdmyt/yaspin/blob/master/yaspin/data/spinners.json

    This only contains some basic ones thats ready to use. For more patterns, checkout the
    URL above.

    Examples:
        >>> from InquirerPy import inquirer
        >>> from InquirerPy.spinner import SPINNERS
        >>> inquirer.select(message="", choices=lambda _: [1, 2, 3], spinner_pattern=SPINNERS.dots)
    """

    dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    dots2 = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    line = ["-", "\\", "|", "/"]
    line2 = ["⠂", "-", "–", "—", "–", "-"]
    pipe = ["┤", "┘", "┴", "└", "├", "┌", "┬", "┐"]
    star = ["✶", "✸", "✹", "✺", "✹", "✷"]
    star2 = ["+", "x", "*"]
    flip = ["_", "_", "_", "-", "`", "`", "'", "´", "-", "_", "_", "_"]
    hamburger = ["☱", "☲", "☴"]
    grow_vertical = ["▁", "▃", "▄", "▅", "▆", "▇", "▆", "▅", "▄", "▃"]
    grow_horizontal = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "▊", "▋", "▌", "▍", "▎"]
    box_bounce = ["▖", "▘", "▝", "▗"]
    triangle = ["◢", "◣", "◤", "◥"]
    arc = ["◜", "◠", "◝", "◞", "◡", "◟"]
    circle = ["◡", "⊙", "◠"]


class SpinnerWindow(ConditionalContainer):
    """Conditional `prompt_toolkit` :class:`~prompt_toolkit.layout.Window` that displays a spinner.

    Args:
        loading: A :class:`~prompt_toolkit.filters.Condition` to indicate if the spinner should be visible.
        redraw: A redraw function (i.e. :meth:`~prompt_toolkit.application.Application.invalidate`) to refresh the UI.
        pattern: List of pattern to display as the spinner.
        delay: Spinner refresh frequency.
        text: Loading text to display.
    """

    def __init__(
        self,
        loading: "Filter",
        redraw: Callable[[], None],
        pattern: Optional[Union[List[str], SPINNERS]] = None,
        delay: float = 0.1,
        text: str = "",
    ) -> None:
        self._loading = to_filter(loading)
        self._spinning = False
        self._redraw = redraw
        self._pattern = pattern or SPINNERS.line
        self._char = self._pattern[0]
        self._delay = delay
        self._text = text or "Loading ..."

        super().__init__(
            content=Window(content=FormattedTextControl(text=self._get_text)),
            filter=self._loading,
        )

    def _get_text(self) -> List[Tuple[str, str]]:
        """Dynamically get the text for the :class:`~prompt_toolkit.layout.Window`.

        Returns:
            Formatted text.
        """
        return [
            ("class:spinner_pattern", self._char),
            ("", " "),
            ("class:spinner_text", self._text),
        ]

    async def start(self) -> None:
        """Start the spinner."""
        if self._spinning:
            return
        self._spinning = True
        while self._loading():
            for char in self._pattern:
                await asyncio.sleep(self._delay)
                self._char = char
                self._redraw()
        self._spinning = False
