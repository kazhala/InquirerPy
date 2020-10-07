"""This module contains the main prompt entrypoint."""
from typing import Any, Dict, Iterable, List, Union

from InquirerPy.exceptions import InvalidArgumentType

questions = [{"type": "confirm", "name": "hello", "question": "adfasfadsfasd"}]


def prompt(
    questions: Iterable[Dict[str, Any]]
) -> Dict[str, Union[str, List[str], bool]]:
    result: Dict[str, Union[str, List[str], bool]] = {}

    if type(questions) != list:
        raise InvalidArgumentType

    return result
