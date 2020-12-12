"""This module contains the main prompt entrypoint."""
import os
from typing import Any, Dict, List, Literal, Optional, Union

from InquirerPy.enum import ACCEPTED_KEYBINDINGS, INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.checkbox import CheckboxPrompt
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.prompts.expand import ExpandPrompt
from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.rawlist import RawlistPrompt
from InquirerPy.prompts.secret import SecretPrompt

question_mapping = {
    "confirm": ConfirmPrompt,
    "filepath": FilePathPrompt,
    "secret": SecretPrompt,
    "input": InputPrompt,
    "list": ListPrompt,
    "checkbox": CheckboxPrompt,
    "rawlist": RawlistPrompt,
    "expand": ExpandPrompt,
}


def prompt(
    questions: List[Dict[str, Any]],
    style: Optional[Dict[str, str]] = None,
    editing_mode: Optional[Literal["default", "vim", "emacs"]] = None,
) -> Dict[str, Optional[Union[str, List[str], bool]]]:
    """Resolve user provided list of questions and get result.

    if "name" param is not present, use the index as the name.

    All param can be controlled via ENV var, if not present, resolver
    will attempt to resolve the value from ENV var.

    A default style is applied using Atom Onedark color if style is not present.

    :param questions: list of questions to ask
    :type questions: List[Dict[str, Any]]
    :param style: the style to apply to the prompt
    :type style: Optional[Dict[str, str]]
    :param editing_mode: the editing_mode to use
    :type editing_mode: Optional[str]
    :return: dictionary of answers
    :rtype: Dict[str, Optional[Union[str, List[str], bool]]]
    """
    result: Dict[str, Optional[Union[str, List[str], bool]]] = {}

    if not isinstance(questions, list):
        raise InvalidArgument("questions should be type of list.")

    if not style:
        style = {
            "questionmark": os.getenv("INQUIRERPY_STYLE_QUESTIONMARK", "#e5c07b"),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
            "input": os.getenv("INQUIRERPY_STYLE_INPUT", "#98c379"),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
            "pointer": os.getenv("INQUIRERPY_STYLE_POINTER", "#61afef"),
            "checkbox": os.getenv("INQUIRERPY_STYLE_CHECKBOX", "#98c379"),
            "separator": os.getenv("INQUIRERPY_STYLE_SEPARATOR", ""),
        }
    if not editing_mode:
        default_mode = os.getenv("INQUIRERPY_EDITING_MODE", "default")
        if default_mode not in ACCEPTED_KEYBINDINGS:
            raise InvalidArgument(
                "INQUIRERPY_EDITING_MODE must be one of 'default' 'emacs' 'vim'."
            )
        else:
            editing_mode = default_mode  # type: ignore

    for i in range(len(questions)):
        try:
            question_type = questions[i].pop("type")
            question_name = questions[i].pop("name", str(i))
            message = questions[i].pop("message")
            if questions[i].get("when") and not questions[i]["when"](result):
                result[question_name] = None
                continue
            result[question_name] = question_mapping[question_type](
                message=message, style=style, editing_mode=editing_mode, **questions[i]
            ).execute()
            if result[question_name] == INQUIRERPY_POINTER_SEQUENCE:
                raise KeyboardInterrupt
        except KeyError:
            raise RequiredKeyNotFound

    return result
