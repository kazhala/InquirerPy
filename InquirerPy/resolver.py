"""This module contains the classic entrypoint for creating prompts.

A `PyInquirer <https://github.com/CITGuru/PyInquirer>`_ compatible entrypoint :func:`.prompt`.
"""
from typing import Any, Dict, List, Optional, Tuple, Union

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.checkbox import CheckboxPrompt
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.prompts.expand import ExpandPrompt
from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.fuzzy import FuzzyPrompt
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.number import NumberPrompt
from InquirerPy.prompts.rawlist import RawlistPrompt
from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.utils import (
    InquirerPyKeybindings,
    InquirerPyQuestions,
    InquirerPySessionResult,
    get_style,
)

__all__ = ["prompt", "prompt_async"]

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
    "number": NumberPrompt,
}


def _get_questions(questions: InquirerPyQuestions) -> List[Dict[str, Any]]:
    """Process and validate questions.

    Args:
        questions: List of questions to create prompt.

    Returns:
        List of validated questions.
    """
    if isinstance(questions, dict):
        questions = [questions]

    if not isinstance(questions, list):
        raise InvalidArgument("argument questions should be type of list or dictionary")

    return questions


def _get_question(
    original_question: Dict[str, Any], result: InquirerPySessionResult, index: int
) -> Tuple[Optional[Dict[str, Any]], str, Union[str, int], str]:
    """Get information from individual question.

    Args:
        original_question: Original question dictionary.
        result: Current prompt session result.
        index: Question index.

    Returns:
        A tuple containing question information in the order of
            question dictionary, type of question, name of question, message of question.
    """
    question = original_question.copy()
    question_type = question.pop("type")
    question_name = question.pop("name", index)
    message = question.pop("message")
    question_when = question.pop("when", None)
    if question_when and not question_when(result):
        result[question_name] = None
        question = None
    return question, question_type, question_name, message


async def prompt_async(
    questions: InquirerPyQuestions,
    style: Optional[Dict[str, str]] = None,
    vi_mode: bool = False,
    raise_keyboard_interrupt: bool = True,
    keybindings: Optional[InquirerPyKeybindings] = None,
    style_override: bool = True,
) -> InquirerPySessionResult:
    """Classic syntax entrypoint to create a prompt session via asynchronous method.

    Refer to :func:`InquirerPy.resolver.prompt` for detailed documentations.
    """
    result: InquirerPySessionResult = {}
    if not keybindings:
        keybindings = {}

    questions = _get_questions(questions=questions)
    question_style = get_style(style, style_override)

    for index, original_question in enumerate(questions):
        try:
            question, question_type, question_name, message = _get_question(
                original_question=original_question, result=result, index=index
            )
            if question is None:
                continue
            args = {
                "message": message,
                "style": question_style,
                "vi_mode": vi_mode,
                "raise_keyboard_interrupt": raise_keyboard_interrupt,
                "session_result": result,
                "keybindings": {**keybindings, **question.pop("keybindings", {})},
            }
            result[question_name] = await question_mapping[question_type](
                **args, **question
            ).execute_async()
        except KeyError:
            raise RequiredKeyNotFound

    return result


def prompt(
    questions: InquirerPyQuestions,
    style: Optional[Dict[str, str]] = None,
    vi_mode: bool = False,
    raise_keyboard_interrupt: bool = True,
    keybindings: Optional[InquirerPyKeybindings] = None,
    style_override: bool = True,
) -> InquirerPySessionResult:
    """Classic syntax entrypoint to create a prompt session.

    Resolve user provided list of questions, display prompts and get the results.

    Args:
        questions: A list of :ref:`pages/prompt:question` to ask. Refer to documentation for more info.
        style: A :class:`dict` containing the style specification for the prompt. Refer to :ref:`pages/style:Style` for more info.
        vi_mode: Use vim keybindings for the prompt instead of the default emacs keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more info.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        keybindings: List of custom :ref:`pages/kb:Keybindings` to apply. Refer to documentation for more info.
        style_override: Override all default styles. When providing any style customisation, all default styles are removed when this is True.

    Returns:
        A dictionary containing all of the question answers. The key is the name of the question and the value is the
        user answer. If the `name` key is not present as part of the question, then the question index will be used
        as the key.

    Raises:
        RequiredKeyNotFound: When the question is missing required keys.
        InvalidArgument: When the provided `questions` argument is not a type of :class:`list` nor :class:`dictionary`.

    Examples:
        >>> from InquirerPy import prompt
        >>> from InquirerPy.validator import NumberValidator
        >>> questions = [
        ...     {
        ...         "type": "input",
        ...         "message": "Enter your age:",
        ...         "validate": NumberValidator(),
        ...         "invalid_message": "Input should be number.",
        ...         "default": "18",
        ...         "name": "age",
        ...         "filter": lambda result: int(result),
        ...         "transformer": lambda result: "Adult" if int(result) >= 18 else "Youth",
        ...     },
        ...     {
        ...         "type": "rawlist",
        ...         "message": "What drinks would you like to buy:",
        ...         "default": 2,
        ...         "choices": lambda result: ["Soda", "Cidr", "Water", "Milk"]
        ...         if result["age"] < 18
        ...         else ["Wine", "Beer"],
        ...         "name": "drink",
        ...     },
        ...     {
        ...         "type": "list",
        ...         "message": "Would you like a bag:",
        ...         "choices": ["Yes", "No"],
        ...         "when": lambda result: result["drink"] in {"Wine", "Beer"},
        ...     },
        ...     {"type": "confirm", "message": "Confirm?", "default": True},
        ... ]
        >>> result = prompt(questions=questions)
    """
    result: InquirerPySessionResult = {}
    if not keybindings:
        keybindings = {}

    questions = _get_questions(questions=questions)
    question_style = get_style(style, style_override)

    for index, original_question in enumerate(questions):
        try:
            question, question_type, question_name, message = _get_question(
                original_question=original_question, result=result, index=index
            )
            if question is None:
                continue
            args = {
                "message": message,
                "style": question_style,
                "vi_mode": vi_mode,
                "raise_keyboard_interrupt": raise_keyboard_interrupt,
                "session_result": result,
                "keybindings": {**keybindings, **question.pop("keybindings", {})},
            }
            result[question_name] = question_mapping[question_type](
                **args, **question
            ).execute()
        except KeyError:
            raise RequiredKeyNotFound

    return result
