"""Module contains the filepath prompt and its completer class."""
import os
from pathlib import Path
from typing import Callable, Dict, Generator, List, Literal, Optional, Tuple, Union

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.keys import Keys
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.shortcuts.prompt import PromptSession
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base import BaseSimplePrompt
from InquirerPy.exceptions import InvalidArgumentType


class FilePathCompleter(Completer):
    """An auto completion class used for prompt session.

    The class structure is defined by prompt_toolkit and is only intended to be used by PromptSession.

    :param only_directories: complete directories only
    :type only_directories: bool
    """

    def __init__(self, only_directories: bool = False):
        """Set base params."""
        self.only_directories = only_directories

    def get_completions(
        self, document, complete_event
    ) -> Generator[Completion, None, None]:
        """Return a completion item (valid file path)."""
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

    def _get_completion(
        self, document, path, validation
    ) -> Generator[Completion, None, None]:
        """Return filepaths based on user input path."""
        for file in path.iterdir():
            if self.only_directories and not os.path.isdir(file):
                continue
            if validation(file, document.text):
                file_name = os.path.basename(file)
                display_name = file_name
                if os.path.isdir(file):
                    display_name = "%s/" % file_name
                yield Completion(
                    "%s" % os.path.basename(str(file)),
                    start_position=-1 * len(os.path.basename(document.text)),
                    display=display_name,
                )


class FilePathPrompt(BaseSimplePrompt):
    """A wrapper class around PromptSession.

    This class is used for filepath prompt.

    :param message: the question to ask
    :type message: str
    :param style: a dictionary of style to apply
    :type style: Dict[str, str]
    :param editing_mode: the mode of editing
    :type editing_mode: Literal['default', 'emacs', 'vim']
    :param default: the default result
    :type default: str
    :param symbol: question symbol to display
    :type symbol: str
    :param validator: a callable or a validation class to validate user input
    :type validator: Optional[Union[Callable[[str], bool], Validator]]
    :param invalid_message: the error message to display when input is invalid
    :type invalid_message: str
    :param only_directories: only complete directories
    :type only_directories: bool
    """

    def __init__(
        self,
        message: str,
        style: Dict[str, str],
        editing_mode: Literal["default", "emacs", "vim"] = "default",
        default: str = "",
        symbol: str = "?",
        validator: Optional[Union[Callable[[str], bool], Validator]] = None,
        invalid_message: str = "Invalid input",
        only_directories: bool = False,
        **kwargs,
    ) -> None:
        """Construct a PromptSession based on parameters and apply key_bindings."""
        super().__init__(
            message,
            style,
            editing_mode=editing_mode,
            symbol=symbol,
            validator=validator,
            invalid_message=invalid_message,
        )
        self.default = default
        if not isinstance(self.default, str):
            raise InvalidArgumentType(
                "default for filepath type question should be type of str."
            )
        self.only_directories = only_directories

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
                self.status["result"] = self.session.default_buffer.text
                self.session.default_buffer.text = ""
                event.app.exit(result=self.status["result"])

        self.session = PromptSession(
            message=self._get_prompt_message,
            key_bindings=self.kb,
            style=self.question_style,
            completer=FilePathCompleter(only_directories=self.only_directories),
            validator=self.validator,
            validate_while_typing=False,
            input=kwargs.pop("input", None),
            output=kwargs.pop("output", None),
            editing_mode=self.editing_mode,
            lexer=SimpleLexer(self.lexer),
        )

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Dynamically update the prompt message.

        Change the user input path to the 'answer' color in style.

        :return: the formatted text for PromptSession
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " ")
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> str:
        """Display the filepath prompt and returns the result.

        :return: user entered filepath
        :rtype: str
        """
        return self.session.prompt(default=self.default)
