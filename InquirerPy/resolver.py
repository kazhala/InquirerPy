"""This module contains the main prompt entrypoint."""
import os
from typing import Any, Dict, List, Optional, Union

from InquirerPy.exceptions import InvalidArgumentType, RequiredKeyNotFound
from InquirerPy.prompts.confirm import Confirm

question_mapping = {"confirm": Confirm}


def prompt(
    questions: List[Dict[str, Any]],
    style: Optional[Dict[str, str]] = None,
    key_binding_mode: Optional[str] = None,
) -> Dict[str, Optional[Union[str, List[str], bool]]]:
    """Resolve user provided list of questions and get result.

    :param questions: list of questions to ask
    :type questions: List[Dict[str, Any]]
    :param style: the style to apply to the prompt
    :type style: Optional[Dict[str, str]]
    :param key_binding_mode: the key_binding_mode to use
    :type key_binding_mode: Optional[str]
    :return: dictionary of answers
    :rtype: Dict[str, Optional[Union[str, List[str], bool]]]
    """
    result: Dict[str, Optional[Union[str, List[str], bool]]] = {}

    if not isinstance(questions, list):
        raise InvalidArgumentType("questions should be type of list.")

    if not style:
        style = {
            "symbol": os.getenv("INQUIRERPY_STYLE_SYMBOL", "#ffcb04"),
            "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
            "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
            "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
        }
    if not key_binding_mode:
        key_binding_mode = os.getenv("INQUIRERPY_KEYBINDING_MODE", "default")

    for i in range(len(questions)):
        try:
            question_type = questions[i].pop("type")
            question_name = questions[i].pop("name", str(i))
            question_content = questions[i].pop("question")
            if questions[i].get("condition") and not questions[i]["condition"](result):
                result[question_name] = None
                continue
            result[question_name] = question_mapping[question_type](
                message=question_content,
                style=style,
                key_binding_mode=key_binding_mode,
                **questions[i]
            ).execute()
        except KeyError:
            raise RequiredKeyNotFound
        except KeyboardInterrupt:
            print("")
            raise

    return result
