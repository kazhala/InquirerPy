"""Module contains the class to create filepath prompt and filepath completer class."""
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator, Optional

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.completion.base import ThreadedCompleter

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

__all__ = ["FilePathPrompt", "FilePathCompleter"]


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
        self._delimiter = "/" if os.name == "posix" else "\\"

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
            dirname = Path(os.path.dirname(f"{Path.home()}{document.text[1:]}"))
            validation = lambda file, doc_text: str(file).startswith(
                f"{Path.home()}{doc_text[1:]}"
            )
        elif document.text.startswith(f".{self._delimiter}"):
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
                    display_name = f"{file_name}{self._delimiter}"
                yield Completion(
                    file.name,
                    start_position=-1 * len(os.path.basename(document.text)),
                    display=display_name,
                )


class FilePathPrompt(InputPrompt):
    """Create a prompt that provides auto completion for system filepaths.

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
        multicolumn_complete: Change the auto-completion UI to a multi column display.
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
        only_directories: Only complete directories.
        only_files: Only complete files.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.
        input: Used internally and will be removed in future updates.
        output: Used internally and will be removed in future updates.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.filepath(message="Enter a path:").execute()
        >>> print(result)
        /home/ubuntu/README.md
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        default: InquirerPyDefault = "",
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        long_instruction: str = "",
        multicolumn_complete: bool = False,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        only_directories: bool = False,
        only_files: bool = False,
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
            keybindings=keybindings,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
            input=input,
            output=output,
        )
