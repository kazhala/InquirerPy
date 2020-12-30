"""Module contains the class to create a secret prompt."""
from typing import Any, Callable, Dict, List, Tuple, Union

from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.input import InputPrompt


class SecretPrompt(InputPrompt):
    """A wrapper class around PromptSession to create a secret prompt.

    :param message: the message to display in the prompt
    :type message: str
    :param style: style to apply to the prompt
    :type style: Dict[str, str]
    :param default: the default value
    :type default: str
    :param qmark: qmark to display infront of the question
    :type qmark: str
    :param editing_mode: the key binding mode to use
    :type editing_mode: str
    :param validate: a callable to validate the user input
    :type validate: Optional[Union[Validator, Callable[[str], bool]]]
    :param invalid_message: the error message to display when validator failed
    :type invalid_message: str
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[str], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[Any], Any]
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str] = None,
        default: str = "",
        qmark: str = "?",
        editing_mode: str = "default",
        validate: Union[Validator, Callable[[str], bool]] = None,
        invalid_message: str = "Invalid input",
        transformer: Callable[[str], Any] = None,
        filter: Callable[[Any], Any] = None,
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
            editing_mode=editing_mode,
            default=default,
            qmark=qmark,
            validate=validate,
            invalid_message=invalid_message,
            is_password=True,
            transformer=transformer,
            filter=filter,
            **kwargs
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get formatted message to display in prompt.

        :return: a list of formatted message
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " ")
        if not self._transformer:
            post_answer = (
                "class:answer",
                ""
                if not self.status["result"]
                else " %s" % "".join(["*" for _ in self.status["result"]]),
            )
        else:
            post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)
