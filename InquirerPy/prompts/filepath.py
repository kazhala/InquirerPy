import os
from pathlib import Path
from typing import Callable, Dict, Optional, Union

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.keys import Keys
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgumentType

accepted_keybindings = {
    "default": EditingMode.EMACS,
    "emacs": EditingMode.EMACS,
    "vim": EditingMode.VI,
}


class FilePathCompleter(Completer):
    def get_completions(self, document, complete_event):
        if document.cursor_position == 0 or document.text == "~":
            return

        validation = lambda file, doc_text: str(file).startswith(doc_text)

        if document.text.startswith("~"):
            dirname = os.path.dirname("%s%s" % (Path.home(), document.text[1:]))
            validation = lambda file, doc_text: str(file).startswith(
                "%s%s" % (Path.home(), doc_text[1:])
            )
        elif document.text.startswith("./"):
            dirname = os.path.curdir
            validation = lambda file, doc_text: str(file).startswith(doc_text[2:])
        else:
            dirname = os.path.dirname(document.text)
        path = Path(dirname)

        for item in self._get_completion(document, path, validation):
            yield item

    def _get_completion(self, document, path, validation):
        for file in path.iterdir():
            if validation(file, document.text):
                yield Completion(
                    "%s" % os.path.basename(str(file)),
                    start_position=-1 * len(os.path.basename(document.text)),
                )


class FilePath(BaseSimplePrompt):
    def __init__(
        self,
        message: str,
        style: Dict[str, str],
        default: str = "",
        symbol: str = "?",
        editing_mode: str = "default",
        validator: Optional[Union[Callable[[str], bool], Validator]] = None,
        invalid_message: str = "Invalid input",
        **kwargs,
    ):
        super().__init__(message, style, symbol)
        self.default = default
        if not isinstance(self.default, str):
            raise InvalidArgumentType(
                "default for filepath type question should be type of str."
            )
        try:
            self.editing_mode = accepted_keybindings[editing_mode]
        except KeyError:
            raise InvalidArgumentType(
                "editing_mode must be one of 'default' 'emacs' 'vim'."
            )
        if isinstance(validator, Validator):
            self.validator = validator
        else:
            self.validator = Validator.from_callable(
                validator if validator else lambda x: True,
                invalid_message,
                move_cursor_to_end=True,
            )

        @self.kb.add("c-space")
        def _(event):
            buff = event.app.current_buffer
            if buff.complete_state:
                buff.complete_next()
            else:
                buff.start_completion(select_first=False)

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
            style=self.question_style,
            completer=FilePathCompleter(),
            validator=self.validator,
            validate_while_typing=False,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
            editing_mode=self.editing_mode,
        )

    def _get_prompt_message(self):
        pre_answer = ("class:instruction", " ")
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self):
        return self.session.prompt()
