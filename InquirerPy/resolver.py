"""This module contains the main prompt entrypoint."""
import os
from typing import Any, Dict, List, Union

from InquirerPy.exceptions import InvalidArgumentType, RequiredKeyNotFound
from InquirerPy.prompts.confirm import Confirm

DEFAULT_STYLE = {
    "symbol": os.getenv("INQUIRERPY_STYLE_SYMBOL", "#ffcb04"),
    "answer": os.getenv("INQUIRERPY_STYLE_ANSWER", "#61afef"),
    "question": os.getenv("INQUIRERPY_STYLE_QUESTION", ""),
    "instruction": os.getenv("INQUIRERPY_STYLE_INSTRUCTION", ""),
}

DEFAULT_KEYBINDING_MODE = os.getenv("INQUIRERPY_KEYBINDING_MODE", "default")

question_mapping = {"confirm": Confirm}


def prompt(questions: List[Dict[str, Any]]) -> Dict[str, Union[str, List[str], bool]]:
    """Resolve user provided list of questions and get result.

    :param questions: list of questions to ask
    :type questions: List[Dict[str, Any]]
    :return: dictionary of answers
    :rtype: Dict[str, Union[str, List[str], bool]]
    """
    result: Dict[str, Union[str, List[str], bool]] = {}

    if not isinstance(questions, list):
        raise InvalidArgumentType("questions should be type of list.")

    for i in range(len(questions)):
        try:
            question_type = questions[i].pop("type")
            question_name = questions[i].pop("name", str(i))
            question_content = questions[i].pop("question")
            question_style = questions[i].pop("style", DEFAULT_STYLE)
            if questions[i].get("condition") and not questions[i]["condition"](result):
                continue
            if not questions[i].get("keybinding"):
                questions[i]["keybinding"] = DEFAULT_KEYBINDING_MODE
            result[question_name] = question_mapping[question_type](
                message=question_content, style=question_style, **questions[i]
            ).execute()
        except KeyError:
            raise RequiredKeyNotFound
        except KeyboardInterrupt:
            print("")
            raise

    return result
