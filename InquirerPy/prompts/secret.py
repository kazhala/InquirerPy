from typing import Callable, Dict, Literal, Optional, Union

from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgumentType


class Secret(BaseSimplePrompt):
    def __init__(
        self,
        message: str,
        style: Dict[str, str],
        default: str = "",
        symbol: str = "?",
        editing_mode: Literal["default", "vim", "emacs"] = "default",
        validator: Optional[Union[Validator, Callable[[str], bool]]] = None,
        invalid_message: str = "Invalid input",
        **kwargs
    ) -> None:
        super().__init__(
            message,
            style,
            editing_mode,
            symbol,
            validator=validator,
            invalid_message=invalid_message,
        )
        self.default = default
        if not isinstance(self.default, str):
            raise InvalidArgumentType(
                "default for filepath type question should be type of str."
            )

        @self.kb.add(Keys.Enter)
        def _(event):
            try:
                self.session.validator.validate(self.session.default_buffer)
            except ValidationError:
                self.session.default_buffer.validate_and_handle()
            else:
                self.status["answered"] = True
                self.status["result"] = (
                    self.session.default_buffer.text
                    if self.session.default_buffer.text
                    else self.default
                )
                self.session.default_buffer.text = ""
                event.app.exit(result=self.status["result"])

        self.session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self.kb,
            is_password=True,
            style=self.question_style,
            validator=self.validator,
            validate_while_typing=False,
            editing_mode=self.editing_mode,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
        )

    def _get_prompt_message(self):
        pre_answer = ("class:instruction", " ")
        post_answer = (
            "class:answer",
            ""
            if not self.status["result"]
            else "".join(["*" for _ in self.status["result"]]),
        )
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> None:
        return self.session.prompt()
