"""Module contains shared utility functions and typing aliases."""
import math
import os
import shutil
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

from prompt_toolkit import print_formatted_text
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument

if TYPE_CHECKING:
    from prompt_toolkit.filters.base import FilterOrBool

    from InquirerPy.base.control import Choice

__all__ = [
    "get_style",
    "calculate_height",
    "InquirerPyStyle",
    "patched_print",
    "color_print",
]


class InquirerPyStyle(NamedTuple):
    """`InquirerPy` Style class.

    Used as a helper class to enforce the method `get_style` to be used
    while also avoiding :class:`dict` to be passed into prompts.

    Note:
        The class is an instance of :class:`typing.NamedTuple`.

    Warning:
        You should not directly be using this class besides for type hinting
        purposes. Obtain an instance of this class using :func:`.get_style`.
    """

    dict: Dict[str, str]


InquirerPySessionResult = Dict[Union[str, int], Optional[Union[str, bool, List[Any]]]]
InquirerPyChoice = Union[List[Any], List["Choice"], List[Dict[str, Any]]]
InquirerPyListChoices = Union[
    Callable[["InquirerPySessionResult"], InquirerPyChoice],
    InquirerPyChoice,
]
InquirerPyValidate = Union[Callable[[Any], bool], "Validator"]
InquirerPyQuestions = Union[List[Dict[str, Any]], Dict[str, Any]]
InquirerPyMessage = Union[str, Callable[["InquirerPySessionResult"], str]]
InquirerPyDefault = Union[Any, Callable[["InquirerPySessionResult"], Any]]
InquirerPyKeybindings = Dict[
    str, List[Dict[str, Union[str, "FilterOrBool", List[str]]]]
]


def get_style(
    style: Optional[Dict[str, str]] = None, style_override: bool = True
) -> InquirerPyStyle:
    """Obtain an :class:`.InquirerPyStyle` instance which can be consumed by the `style` parameter in prompts.

    Tip:
        This function supports ENV variables.

        For all the color ENV variable names, refer to the :ref:`ENV <pages/env:Style>` documentation.

    Note:
        If no style is provided, then a default theme based on `one dark <https://github.com/joshdick/onedark.vim#color-reference>`_
        color palette is applied.

    Note:
        Priority: style parameter -> ENV variable -> default style

    Args:
        style: The dictionary of style classes and their colors, If nothing is passed, the style will be resolved to the :ref:`pages/style:Default Style`.
        style_override: A boolean to determine if the supplied `style` parameter should be merged with the :ref:`pages/style:Default Style` or override them.
            By default, the supplied style will overwrite the :ref:`pages/style:Default Style`.

    Returns:
        An instance of :class:`.InquirerPyStyle`.

    Examples:
        >>> from InquirerPy import get_style
        >>> from InquirerPy import inquirer
        >>> style = get_style({"questionmark": "#ffffff", "answer": "#000000"}, style_override=False)
        >>> result = inquirer.confirm(message="Confirm?", style=style).execute()
    """
    if not style_override or style is None:
        if not style:
            style = {}
        result = {
            "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", "#e5c07b"),
            "answermark": os.getenv("INQUIRERPY_STYLE_ANSWERMARK", "#e5c07b"),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
            "input": os.getenv("INQUIRERPY_STYLE_INPUT", "#98c379"),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "answered_question": os.getenv("INQUIRERPY_STYLE_ANSWERED_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", "#abb2bf"),
            "long_instruction": os.getenv(
                "INQUIRERPY_STYLE_LONG_INSTRUCTION", "#abb2bf"
            ),
            "pointer": os.getenv("INQUIRERPY_STYLE_POINTER", "#61afef"),
            "checkbox": os.getenv("INQUIRERPY_STYLE_CHECKBOX", "#98c379"),
            "separator": os.getenv("INQUIRERPY_STYLE_SEPARATOR", ""),
            "skipped": os.getenv("INQUIRERPY_STYLE_SKIPPED", "#5c6370"),
            "validator": os.getenv("INQUIRERPY_STYLE_VALIDATOR", ""),
            "marker": os.getenv("INQUIRERPY_STYLE_MARKER", "#e5c07b"),
            "fuzzy_prompt": os.getenv("INQUIRERPY_STYLE_FUZZY_PROMPT", "#c678dd"),
            "fuzzy_info": os.getenv("INQUIRERPY_STYLE_FUZZY_INFO", "#abb2bf"),
            "fuzzy_border": os.getenv("INQUIRERPY_STYLE_FUZZY_BORDER", "#4b5263"),
            "fuzzy_match": os.getenv("INQUIRERPY_STYLE_FUZZY_MATCH", "#c678dd"),
            "spinner_pattern": os.getenv("INQUIRERPY_STYLE_SPINNER_PATTERN", "#e5c07b"),
            "spinner_text": os.getenv("INQUIRERPY_STYLE_SPINNER_TEXT", ""),
            **style,
        }
    else:
        result = {
            "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", ""),
            "answermark": os.getenv("INQUIRERPY_STYLE_ANSWERMARK", ""),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", ""),
            "input": os.getenv("INQUIRERPY_STYLE_INPUT", ""),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "answered_question": os.getenv("INQUIRERPY_STYLE_ANSWERED_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
            "long_instruction": os.getenv("INQUIRERPY_STYLE_LONG_INSTRUCTION", ""),
            "pointer": os.getenv("INQUIRERPY_STYLE_POINTER", ""),
            "checkbox": os.getenv("INQUIRERPY_STYLE_CHECKBOX", ""),
            "separator": os.getenv("INQUIRERPY_STYLE_SEPARATOR", ""),
            "skipped": os.getenv("INQUIRERPY_STYLE_SKIPPED", ""),
            "validator": os.getenv("INQUIRERPY_STYLE_VALIDATOR", ""),
            "marker": os.getenv("INQUIRERPY_STYLE_MARKER", ""),
            "fuzzy_prompt": os.getenv("INQUIRERPY_STYLE_FUZZY_PROMPT", ""),
            "fuzzy_info": os.getenv("INQUIRERPY_STYLE_FUZZY_INFO", ""),
            "fuzzy_border": os.getenv("INQUIRERPY_STYLE_FUZZY_BORDER", ""),
            "fuzzy_match": os.getenv("INQUIRERPY_STYLE_FUZZY_MATCH", ""),
            "spinner_pattern": os.getenv("INQUIRERPY_STYLE_SPINNER_PATTERN", ""),
            "spinner_text": os.getenv("INQUIRERPY_STYLE_SPINNER_TEXT", ""),
            **style,
        }

    if result.get("fuzzy_border"):
        result["frame.border"] = result.pop("fuzzy_border")
    if result.get("validator"):
        result["validation-toolbar"] = result.pop("validator")
    result["bottom-toolbar"] = "noreverse"
    return InquirerPyStyle(result)


def calculate_height(
    height: Optional[Union[int, str]],
    max_height: Optional[Union[int, str]],
    height_offset: int = 2,
) -> Tuple[Optional[int], int]:
    """Calculate the `height` and `max_height` for the main question contents.

    Tip:
        The parameter `height`/`max_height` can be specified by either a :class:`string` or :class:`int`.

        When `height`/`max_height` is :class:`str`:
            It will set the height to a percentage based on the value provided.
            You can optionally add the '%' sign which will be ignored while processing.

            Example: "60%" or "60" (60% of the current terminal visible lines)

        When `height`/`max_height` is :class:`int`:
            It will set the height to exact number of lines based on the value provided.

            Example: 20 (20 lines in terminal)

    Note:
        If `max_height` is not provided or is None, the default `max_height` will be configured to `70%` for
        best visual presentation in the terminal.

    Args:
        height: The desired height in either percentage as string or exact value as int.
        max_height: Maximum acceptable height in either percentage as string or exact value as int.
        height_offset: Height offset to apply to the height.

    Returns:
        A :class:`tuple` with the first value being the desired height and the second value being
        the maximum height.

    Raises:
        InvalidArgument: The provided `height`/`max_height` is not able to to be converted to int.

    Examples:
        >>> calculate_height(height="60%", max_height="100%")
    """
    try:
        _, term_lines = shutil.get_terminal_size()
        term_lines = term_lines
        if not height:
            dimmension_height = None
        else:
            if isinstance(height, str):
                height = height.replace("%", "")
                height = int(height)
                dimmension_height = (
                    math.floor(term_lines * (height / 100)) - height_offset
                )
            else:
                dimmension_height = height

        if not max_height:
            max_height = "70%" if not height else "100%"
        if isinstance(max_height, str):
            max_height = max_height.replace("%", "")
            max_height = int(max_height)
            dimmension_max_height = (
                math.floor(term_lines * (max_height / 100)) - height_offset
            )
        else:
            dimmension_max_height = max_height

        if dimmension_height and dimmension_height > dimmension_max_height:
            dimmension_height = dimmension_max_height
        if dimmension_height and dimmension_height <= 0:
            dimmension_height = 1
        if dimmension_max_height <= 0:
            dimmension_max_height = 1
        return dimmension_height, dimmension_max_height

    except ValueError:
        raise InvalidArgument(
            "prompt argument height/max_height needs to be type of an int or str"
        )


def patched_print(*values) -> None:
    """Patched :func:`print` that can print values without interrupting the prompt.

    See Also:
        :func:`print`
        :func:`~prompt_toolkit.application.run_in_terminal`

    Args:
        *values: Refer to :func:`print`.

    Examples:
        >>> patched_print("Hello World")
    """

    def _print():
        print(*values)

    run_in_terminal(_print)


def color_print(
    formatted_text: List[Tuple[str, str]], style: Optional[Dict[str, str]] = None
) -> None:
    """Print colored text leveraging :func:`~prompt_toolkit.shortcuts.print_formatted_text`.

    This function automatically handles printing the text without interrupting the
    current prompt.

    Args:
        formatted_text: A list of formatted_text.
        style: Style to apply to `formatted_text` in :class:`dictionary` form.

    Example:
        >>> color_print(formatted_text=[("class:aa", "hello "), ("class:bb", "world")], style={"aa": "red", "bb": "blue"})
        >>> color_print([("red", "yes"), ("", " "), ("blue", "no")])
    """

    def _print():
        print_formatted_text(
            FormattedText(formatted_text),
            style=Style.from_dict(style) if style else None,
        )

    if get_app().is_running:
        run_in_terminal(_print)
    else:
        _print()
