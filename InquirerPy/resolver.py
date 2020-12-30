"""This module contains the main prompt entrypoint."""
import os
from typing import Any, Dict, List, Optional, Union

from prompt_toolkit.filters.base import FilterOrBool

from InquirerPy.enum import ACCEPTED_KEYBINDINGS, INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.checkbox import CheckboxPrompt
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.prompts.expand import ExpandPrompt
from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.fuzzy import FuzzyPrompt
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.rawlist import RawlistPrompt
from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.utils import get_style

__all__ = ["prompt"]

question_mapping = {
    "confirm": ConfirmPrompt,
    "filepath": FilePathPrompt,
    "secret": SecretPrompt,
    "input": InputPrompt,
    "list": ListPrompt,
    "checkbox": CheckboxPrompt,
    "rawlist": RawlistPrompt,
    "expand": ExpandPrompt,
    "fuzzy": FuzzyPrompt,
}

list_prompts = {"list", "checkbox", "rawlist", "expand", "fuzzy"}


def prompt(
    questions: List[Dict[str, Any]],
    style: Dict[str, str] = None,
    editing_mode: str = None,
    raise_keyboard_interrupt: bool = True,
    keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
    style_override: bool = False,
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
    :type editing_mode: str
    :param raise_keyboard_interrupt: raise the kbi exception when user hit c-c
        If false, store result as None and continue
    :type raise_keyboard_interrupt: bool
    :param keybindings: custom keybindings to apply
    :type keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]]
    :param style_override: override all default styles
    :type style_override: bool
    :return: dictionary of answers
    :rtype: Dict[str, Optional[Union[str, List[str], bool]]]
    """
    result: Dict[str, Optional[Union[str, List[str], bool]]] = {}
    if not keybindings:
        keybindings = {}

    if not isinstance(questions, list):
        raise InvalidArgument("questions should be type of list.")

    style = get_style(style, style_override)
    if not editing_mode:
        default_mode = os.getenv("INQUIRERPY_EDITING_MODE", "default")
        if default_mode not in ACCEPTED_KEYBINDINGS:
            raise InvalidArgument(
                "INQUIRERPY_EDITING_MODE must be one of 'default' 'emacs' 'vim'."
            )
        else:
            editing_mode = default_mode

    for index, question in enumerate(questions):
        try:
            question_type = question.pop("type")
            question_name = question.pop("name", str(index))
            message = question.pop("message")
            if question.get("when") and not question["when"](result):
                result[question_name] = None
                continue
            args = {"message": message, "style": style, "editing_mode": editing_mode}
            if question_type in list_prompts:
                args["keybindings"] = {**keybindings, **question.pop("keybindings", {})}
            result[question_name] = question_mapping[question_type](
                **args, **question
            ).execute()
            if result[question_name] == INQUIRERPY_KEYBOARD_INTERRUPT:
                if raise_keyboard_interrupt:
                    raise KeyboardInterrupt
                else:
                    result[question_name] = None
        except KeyError:
            raise RequiredKeyNotFound

    return result
