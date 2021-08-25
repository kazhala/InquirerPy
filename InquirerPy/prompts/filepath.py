"""Module contains the class to create filepath prompt and filepath completer class."""
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator, Union

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.base import ThreadedCompleter
from prompt_toolkit.validation import Validator

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import InquirerPyStyle, SessionResult

if TYPE_CHECKING:
    from prompt_toolkit.input.base import Input
    from prompt_toolkit.output.base import Output

__all__ = ["FilePathPrompt"]


class FilePathCompleter(Completer):
    """An auto completion class which generates system filepath.

    See Also:
        :class:`~prompt_toolkit.completion.Completer`

    Args:
        only_directories: Only complete directories.
        only_files: Only complete files.
    """

    def __init__(self, only_directories: bool = False, only_files: bool = False):
        self._only_directories = only_directories
        self._only_files = only_files

    def get_completions(
        self, document, complete_event
    ) -> Generator[Completion, None, None]:
        """Get a list of valid system paths."""
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
    """A wrapper class around :class:`~prompt_toolkit.shortcuts.PromptSession`.

    Create a prompt that provides auto completion for system filepaths.

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
        validate: Validation callable or class to validate user input.
        invalid_message: Error message to display when input is invalid.
        transformer: A callable to transform the result that gets printed in the terminal.
            This is visual effect only.
        filter: A callable to filter the result that gets returned.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        only_directories: Only complete directories.
        only_files: Only complete files.
        session_result: Used for `classic syntax`, ignore this argument.
        input: Used for testing, ignore this argument.
        output: Used for testing, ignore this argument.

    Examples:
        >>> result = FilePathPrompt(message="Enter a path:").execute()
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
        input: "Input" = None,
        output: "Output" = None,
    ) -> None:
        if not isinstance(default, str):
            raise InvalidArgument(
                "filepath prompt argument default should be type of str"
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
            input=input,
            output=output,
        )
