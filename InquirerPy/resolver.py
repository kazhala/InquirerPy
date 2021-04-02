"""This module contains the main prompt entrypoint."""
from typing import Any, Dict, List, Union

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
from InquirerPy.utils import SessionResult, get_style

__all__ = ["prompt"]

question_mapping = {
    "confirm": ConfirmPrompt,
    "filepath": FilePathPrompt,
    "password": SecretPrompt,
    "input": InputPrompt,
    "list": ListPrompt,
    "checkbox": CheckboxPrompt,
    "rawlist": RawlistPrompt,
    "expand": ExpandPrompt,
    "fuzzy": FuzzyPrompt,
}

list_prompts = {"list", "checkbox", "rawlist", "expand", "fuzzy"}


def prompt(
    questions: Union[List[Dict[str, Any]], Dict[str, Any]],
    style: Dict[str, str] = None,
    vi_mode: bool = False,
    raise_keyboard_interrupt: bool = True,
    keybindings: Dict[str, List[Dict[str, Any]]] = None,
    style_override: bool = True,
) -> SessionResult:
    """Resolve user provided list of questions and get result.

    if "name" param is not present, use the index as the name.

    All param can be controlled via ENV var, if not present, resolver
    will attempt to resolve the value from ENV var.

    A default style is applied using Atom Onedark color if style is not present.

    :param questions: list of questions to ask
        if only one question is needed, providing a single dict is also sufficent
    :type questions: Union[List[Dict[str, Any]], Dict[str, Any]]
    :param style: the style to apply to the prompt
    :type style: Dict[str, str]
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: bool
    :param raise_keyboard_interrupt: raise the kbi exception when user hit c-c
        If false, store result as None and continue
    :type raise_keyboard_interrupt: bool
    :param keybindings: custom keybindings to apply
    :type keybindings: Dict[str, List[Dict[str, Any]]]
    :param style_override: override all default styles
    :type style_override: bool
    :return: dictionary of answers
    :rtype: SessionResult
    """
    result: SessionResult = {}
    if not keybindings:
        keybindings = {}

    if isinstance(questions, dict):
        questions = [questions]

    if not isinstance(questions, list):
        raise InvalidArgument("questions should be type of list.")

    question_style = get_style(style, style_override)

    for index, original_question in enumerate(questions):
        try:
            question = original_question.copy()
            question_type = question.pop("type")
            question_name = question.pop("name", index)
            message = question.pop("message")
            question_when = question.pop("when", None)
            if question_when and not question_when(result):
                result[question_name] = None
                continue
            args = {
                "message": message,
                "style": question_style,
                "vi_mode": vi_mode,
                "session_result": result,
            }
            if question_type in list_prompts:
                args["keybindings"] = {**keybindings, **question.pop("keybindings", {})}
            result[question_name] = question_mapping[question_type](
                **args, **question
            ).execute(raise_keyboard_interrupt=raise_keyboard_interrupt)
        except KeyError:
            raise RequiredKeyNotFound

    return result
