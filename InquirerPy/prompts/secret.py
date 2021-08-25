"""Module contains the class to create a secret prompt."""
from typing import TYPE_CHECKING, Any, Callable, List, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import InquirerPyStyle, SessionResult

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.output.base import Output

__all__ = ["SecretPrompt"]


class SecretPrompt(InputPrompt):
    """A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Create a prompt that accepts user input while transforming the text to asterisks.

    Args:
        message: The question to ask the user.
        style: A dictionary of style to apply. Refer to :ref:`pages/style:Style`.
        vi_mode: Use vim keybinding for the prompt.
        default: The default text value to add to the input.
        qmark: Custom symbol that will be displayed infront of the question before its answered.
        amark: Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the `message`.
        completer: Auto completer to add to the input prompt.
        multicolumn_complete: Complete in multi column.
        multiline: Enable multiline mode.
        validate: Validation callable or class to validate user input.
        invalid_message: Error message to display when input is invalid.
        transformer: A callable to transform the result that gets printed in the terminal.
            This is visual effect only.
        filter: A callable to filter the result that gets returned.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        session_result: Used for `classic syntax`, ignore this argument.
        input: Used for testing, ignore this argument.
        output: Used for testing, ignore this argument.

    Examples:
        >>> result = SecretPrompt(message="Password:").execute()
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
        input: "Input" = None,
        output: "Output" = None,
    ) -> None:
        if not isinstance(default, str):
            raise InvalidArgument(
                "secret prompt argument default should be type of str"
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
            input=input,
            output=output,
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get message to display infront of the input buffer.

        Args:
            pre_answer: The formatted text to display before answering the question.
            post_answer: The formatted text to display after answering the question.

        Returns:
            Formatted text in list of tuple format.
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
