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


class FilePathCompleter(Completer):
    """An auto completion class used for prompt session.

    The class structure is defined by prompt_toolkit and is only intended to be used by PromptSession.

    :param only_directories: complete directories only
    :type only_directories: bool
    """

    def __init__(self, only_directories: bool = False, only_files: bool = False):
        """Set base params."""
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

    :param message: the question to ask
    :type message: Union[str, Callable[[SessionResult], str]]
    :param style: a dictionary of style to apply
    :type style: InquirerPyStyle
    :param vi_mode: use vi kb for the prompt
    :type vi_mode: bool
    :param default: the default result
    :type default: Union[str, Callable[[SessionResult], str]]
    :param qmark: question qmark to display
    :type qmark: str
    :param multicolumn_complete: complete in multi column
    :type multicolumn_complete: bool
    :param validate: a callable or a validation class to validate user input
    :type validate: Union[Callable[[str], bool], Validator]
    :param invalid_message: the error message to display when input is invalid
    :type invalid_message: str
    :param only_directories: only complete directories
    :type only_directories: bool
    :param only_files: only complete files
    :type only_files: bool
    :param transformer: a callable to transform the result, this is visual effect only
    :type transformer: Callable[[str], Any]
    :param filter: a callable to filter the result, updating the user input before returning the result
    :type filter: Callable[[str], Any]
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        default: Union[str, Callable[[SessionResult], str]] = "",
        qmark: str = "?",
        multicolumn_complete: bool = False,
        validate: Union[Callable[[str], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        only_directories: bool = False,
        only_files: bool = False,
        transformer: Callable[[str], Any] = None,
        filter: Callable[[str], Any] = None,
        session_result: SessionResult = None,
        **kwargs,
    ) -> None:
        """Construct a PromptSession based on parameters and apply key_bindings."""
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
            session_result=session_result,
            **kwargs,
        )
