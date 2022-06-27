"""Module contains the class to create a secret prompt."""
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
)

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.output.base import Output

__all__ = ["SecretPrompt"]


class SecretPrompt(InputPrompt):
    """Create a text prompt which transforms the input to asterisks while typing.

    A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default text value of the prompt.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        instruction: Short instruction to display next to the question.
        long_instruction: Long instructions to display at the bottom of the prompt.
        validate: Add validation to user input.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        invalid_message: Error message to display when user input is invalid.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        transformer: A function which performs additional transformation on the value that gets printed to the terminal.
            Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:transformer` documentation for more details.
        filter: A function which performs additional transformation on the result.
            This affects the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:filter` documentation for more details.
        keybindings: Customise the builtin keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more details.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.
        input: Used internally and will be removed in future updates.
        output: Used internally and will be removed in future updates.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.secret(message="Password:").execute()
        >>> print(f"Password: {result}")
        Password: asdf123
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        default: InquirerPyDefault = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        vi_mode: bool = False,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        transformer: Optional[Callable[[str], Any]] = None,
        filter: Optional[Callable[[str], Any]] = None,
        keybindings: Optional[InquirerPyKeybindings] = None,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
        input: Optional["Input"] = None,
        output: Optional["Output"] = None,
    ) -> None:
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            default=default,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            long_instruction=long_instruction,
            validate=validate,
            invalid_message=invalid_message,
            is_password=True,
            transformer=transformer,
            filter=filter,
            keybindings=keybindings,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
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
