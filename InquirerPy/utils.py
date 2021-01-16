"""Module contains shared utility functions."""
import math
import os
import shutil
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, Union

from prompt_toolkit import print_formatted_text
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

from InquirerPy.exceptions import InvalidArgument

__all__ = ["get_style", "calculate_height", "InquirerPyStyle"]


class InquirerPyStyle(NamedTuple):
    """InquirerPy style class.

    Enforce the method `get_style` to be used, avoiding
    direct dict passed into prompts.
    """

    dict: Dict[str, str]


SessionResult = Dict[Union[str, int], Optional[Union[str, bool, List[Any]]]]


def get_style(
    style: Dict[str, str] = None, style_override: bool = True
) -> InquirerPyStyle:
    """Get default style if style parameter is missing.

    Reads the ENV variable first before apply default one dark theme.

    Priority:
    style parameter -> ENV variable -> default style

    :param style: style to apply to prompt
    :type style: Dict[str, str]
    :param style_override: override all default styles
    :type style_override: bool
    :return: instance of InquirerPyStyle, consume it via `Style.from_dict(InquirerPyStyle.dict)`
    :rtype: InquirerPyStyle
    """
    if not style_override or style is None:
        if not style:
            style = {}
        result = {
            "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", "#e5c07b"),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
            "input": os.getenv("INQUIRERPY_STYLE_INPUT", "#98c379"),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
            "pointer": os.getenv("INQUIRERPY_STYLE_POINTER", "#61afef"),
            "checkbox": os.getenv("INQUIRERPY_STYLE_CHECKBOX", "#98c379"),
            "separator": os.getenv("INQUIRERPY_STYLE_SEPARATOR", ""),
            "skipped": os.getenv("INQUIRERPY_STYLE_SKIPPED", "#5c6370"),
            "validator": os.getenv("INQUIRERPY_STYLE_VALIDATOR", ""),
            "marker": os.getenv("INQUIRERPY_STYLE_MARKER", "#e5c07b"),
            "fuzzy_prompt": os.getenv("INQUIRERPY_STYLE_FUZZY_PROMPT", "#c678dd"),
            "fuzzy_info": os.getenv("INQUIRERPY_STYLE_FUZZY_INFO", "#56b6c2"),
            "fuzzy_border": os.getenv("INQUIRERPY_STYLE_FUZZY_BORDER", "#4b5263"),
            "fuzzy_match": os.getenv("INQUIRERPY_STYLE_FUZZY_MATCH", "#c678dd"),
            **style,
        }
    else:
        result = {
            "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", ""),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", ""),
            "input": os.getenv("INQUIRERPY_STYLE_INPUT", ""),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
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
            **style,
        }

    if result.get("fuzzy_border"):
        result["frame.border"] = result.pop("fuzzy_border")
    if result.get("validator"):
        result["validation-toolbar"] = result.pop("validator")
    return InquirerPyStyle(result)


def calculate_height(
    height: Optional[Union[int, str]],
    max_height: Optional[Union[int, str]],
    offset: int = 2,
) -> Tuple[Optional[int], int]:
    """Calculate the height and max_height for the choice window.

    Allowed height values:
    * "60%" - percentage height in str
    * 20 - exact line height in int

    If max_height is not provided or is None,
    set it to `60%` for best visual presentation in terminal.
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
                dimmension_height = math.floor(term_lines * (height / 100)) - offset
            else:
                dimmension_height = height

        if not max_height:
            max_height = "60%" if not height else "100%"
        if isinstance(max_height, str):
            max_height = max_height.replace("%", "")
            max_height = int(max_height)
            dimmension_max_height = math.floor(term_lines * (max_height / 100)) - offset
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
            "prompt height needs to be either an int or str representing height percentage."
        )


def patched_print(*values) -> None:
    """Print the values without interrupting the prompt."""

    def _print():
        print(*values)

    run_in_terminal(_print)


def color_print(
    formatted_text: List[Tuple[str, str]], style: Dict[str, str] = None
) -> None:
    """Print colored text.

    This is a wrapper around `prompt_toolkit` `print_formatted_text`.
    It automatically handles printing the text without interrupting the
    current prompt.

    :param formatted_text: a list of formatted text
        [("class:aa", "Hello")] or [("#ffffff", "Hello")]
    :type formatted_text: List[Tuple[str, str]]
    :param style: a dictionary of style
    :type style: Dict[str, str]
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
