"""Module contains shared utility functions."""

import os
from typing import Dict


def get_style() -> Dict[str, str]:
    """Get default style if style parameter is missing.

    Reads the ENV variable first before apply default one dark theme.

    :return: style dictionary ready to be consumed by `Style.from_dict`
    :rtype: Dict[str, str]
    """
    return {
        "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", "#e5c07b"),
        "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
        "input": os.getenv("INQUIRERPY_STYLE_INPUT", "#98c379"),
        "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
        "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
        "pointer": os.getenv("INQUIRERPY_STYLE_POINTER", "#61afef"),
        "checkbox": os.getenv("INQUIRERPY_STYLE_CHECKBOX", "#98c379"),
        "separator": os.getenv("INQUIRERPY_STYLE_SEPARATOR", ""),
        "skipped": os.getenv("INQUIRERPY_STYLE_SKIPPED", "#5c6370"),
        "fuzzy_text": os.getenv("INQUIRERPY_STYLE_TEXT", "#abb2bf"),
        "fuzzy_prompt": os.getenv("INQUIRERPY_STYLE_FUZZY_PROMPT", "#c678dd"),
        "fuzzy_info": os.getenv("INQUIRERPY_STYLE_FUZZY_INFO", "#98c379"),
        "fuzzy_marker": os.getenv("INQUIRERPY_STYLE_FUZZY_MARKER", "#e5c07b"),
        "fuzzy_border": os.getenv("INQUIRERPY_STYLE_FUZZY_BORDER", "#4b5263"),
    }
