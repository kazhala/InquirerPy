"""Module contains the class to create a secret prompt."""
from typing import Any, Callable, List, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["SecretPrompt"]


class SecretPrompt(InputPrompt):
    """A wrapper class around PromptSession to create a secret prompt.

    :param message: The message to display in the prompt.
    :param style: The style to apply to the prompt.
    :param default: The default value.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param instruction: Instruction to display after the question message.
    :param vi_mode: Use vi kb for the prompt.
    :param validate: A callable to validate the user input.
    :param invalid_message: The error message to display when validator failed.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        default: Union[str, Callable[[SessionResult], str]] = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        vi_mode: bool = False,
        validate: Union[Validator, Callable[[str], bool]] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[str], Any] = None,
        filter: Callable[[str], Any] = None,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
        **kwargs
    ) -> None:
        """Construct the prompt session."""
        if not isinstance(default, str):
            raise InvalidArgument(
                "default for secret type question should be type of str."
            )
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            default=default,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            validate=validate,
            invalid_message=invalid_message,
            is_password=True,
            transformer=transformer,
            filter=filter,
            wrap_lines=wrap_lines,
            session_result=session_result,
            **kwargs
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get formatted message to display in prompt.

        :return: A list of formatted message.
        """
        pre_answer = (
            "class:instruction",
            " %s " % self.instruction if self.instruction else " ",
        )
        post_answer = (
            "class:answer",
            ""
            if not self.status["result"]
            else " %s" % "".join(["*" for _ in self.status["result"]]),
        )
        return super()._get_prompt_message(pre_answer, post_answer)
