"""Module contains the filepath prompt and its completer class."""
import os
from pathlib import Path
from typing import Any, Callable, Generator, Union

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.base import ThreadedCompleter
from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import InquirerPyStyle, SessionResult

__all__ = ["FilePathPrompt"]


class FilePathCompleter(Completer):
    """An auto completion class used for prompt session.

    The class structure is defined by prompt_toolkit and is only intended to be used by PromptSession.

    :param only_directories: Complete directories only.
    """

    def __init__(self, only_directories: bool = False, only_files: bool = False):
        self._only_directories = only_directories
        self._only_files = only_files

    def get_completions(
        self, document, complete_event
    ) -> Generator[Completion, None, None]:
        """Return a completion item (valid file path)."""
        if document.text == "~":
            return

        validation = lambda file, doc_text: str(file).startswith(doc_text)

        if document.cursor_position == 0:
            dirname = Path.cwd()
            validation = lambda file, doc_text: True
        elif document.text.startswith("~"):
            dirname = Path(os.path.dirname("%s%s" % (Path.home(), document.text[1:])))
            validation = lambda file, doc_text: str(file).startswith(
                "%s%s" % (Path.home(), doc_text[1:])
            )
        elif document.text.startswith("./"):
            dirname = Path(os.path.dirname(document.text))
            validation = lambda file, doc_text: str(file).startswith(doc_text[2:])
        else:
            dirname = Path(os.path.dirname(document.text))

        for item in self._get_completion(document, dirname, validation):
            yield item

    def _get_completion(
        self, document, path, validation
    ) -> Generator[Completion, None, None]:
        """Return filepaths based on user input path."""
        if not path.is_dir():
            return
        for file in path.iterdir():
            if self._only_directories and not file.is_dir():
                continue
            if self._only_files and not file.is_file():
                continue
            if validation(file, document.text):
                file_name = file.name
                display_name = file_name
                if file.is_dir():
                    display_name = "%s/" % file_name
                yield Completion(
                    "%s" % file.name,
                    start_position=-1 * len(os.path.basename(document.text)),
                    display=display_name,
                )


class FilePathPrompt(InputPrompt):
    """A wrapper class around PromptSession.

    This class is used for filepath prompt.

    :param message: The question to ask.
    :param style: A dictionary of style to apply.
    :param vi_mode: Use vi kb for the prompt.
    :param default: The default result.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: The custom symbol to display infront of the question after its answered.
    :param instruction: Instruction to display after the question message.
    :param multicolumn_complete: Complete in multi column.
    :param validate: A callable or a validation class to validate user input.
    :param invalid_message: The error message to display when input is invalid.
    :param only_directories: Only complete directories.
    :param only_files: Only complete files.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        default: Union[str, Callable[[SessionResult], str]] = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        multicolumn_complete: bool = False,
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        only_directories: bool = False,
        only_files: bool = False,
        transformer: Callable[[str], Any] = None,
        filter: Callable[[str], Any] = None,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
        **kwargs,
    ) -> None:
        if not isinstance(default, str):
            raise InvalidArgument(
                "default for filepath type question should be type of str."
            )
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            default=default,
            qmark=qmark,
            amark=amark,
            instruction=instruction,
            completer=ThreadedCompleter(
                FilePathCompleter(
                    only_directories=only_directories, only_files=only_files
                )
            ),
            multicolumn_complete=multicolumn_complete,
            validate=validate,
            invalid_message=invalid_message,
            transformer=transformer,
            filter=filter,
            wrap_lines=wrap_lines,
            session_result=session_result,
            **kwargs,
        )
