"""This module contains the main prompt entrypoint."""
from typing import Any, Dict, List, Union

from InquirerPy.exceptions import InvalidArgumentType, RequiredKeyNotFound
from InquirerPy.prompts.confirm import Confirm

DEFAULT_STYLE = {
    "symbol": "#5F819D",
    "answer": "#FF9D00 bold",
    "question": "bold",
    "instruction": "",
}

question_mapping = {"confirm": Confirm}


def prompt(questions: List[Dict[str, Any]]) -> Dict[str, Union[str, List[str], bool]]:
    """Resolve user provided list of questions and get result.

    :param questions: list of questions to ask
    :type questions: List[Dict[str, Any]]
    :return: dictionary of answers
    :rtype: Dict[str, Union[str, List[str], bool]]
    """
    result: Dict[str, Union[str, List[str], bool]] = {}

    if type(questions) != list:
        raise InvalidArgumentType

    for i in range(len(questions)):
        try:
            question_type = questions[i].pop("type")
            question_name = questions[i].pop("name", str(i))
            question_content = questions[i].pop("question")
            question_style = questions[i].pop("style", DEFAULT_STYLE)
            result[question_name] = question_mapping[question_type](
                message=question_content, style=question_style, **questions[i]
            )()
        except KeyError:
            raise RequiredKeyNotFound
        except KeyboardInterrupt:
            print("")
            raise

    return result
