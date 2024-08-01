import os
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import ANY, call, patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.filepath import FilePathCompleter, FilePathPrompt
from InquirerPy.utils import InquirerPyStyle
from InquirerPy.validator import PathValidator


class TestFilePath(unittest.TestCase):
    def setUp(self):
        self.dirs_to_create = ["dir1", "dir2", "dir3", ".dir"]
        self.files_to_create = ["file1", "file2", "file3", ".file"]
        self.test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @contextmanager
    def chdir(self, directory):
        orig_dir = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(orig_dir)

    def create_temp_files(self):
        for directory in self.dirs_to_create:
            self.test_dir.joinpath(directory).mkdir(exist_ok=True)
        for file in self.files_to_create:
            with self.test_dir.joinpath(file).open("wb") as output_file:
                output_file.write("".encode("UTF-8"))

    def test_completer_explicit_currdir_all(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = "./"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(
                sorted(completions),
                sorted(self.dirs_to_create + self.files_to_create),
            )

    def test_completer_currdir_file(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = "./file"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), ["file1", "file2", "file3"])

    def test_completer_hidden(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = "."
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), [".dir", ".file"])

    def test_completer_normal(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = "dir"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), ["dir1", "dir2", "dir3"])

    def test_completer_expanduser(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = "~/"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertGreater(len(completions), 0)

    def test_completer_dir_only(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter(only_directories=True)
            doc_text = "./"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), sorted(self.dirs_to_create))

    def test_completer_file_only(self):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter(only_files=True)
            doc_text = "./"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), sorted(self.files_to_create))

    def test_input(self):
        with create_pipe_input() as inp:
            inp.send_text("./file1\n")
            filepath_prompt = FilePathPrompt(
                message="hello",
                style=InquirerPyStyle({"qmark": "bold"}),
                input=inp,
                output=DummyOutput(),
            )
            result = filepath_prompt.execute()
            self.assertEqual(result, "./file1")
            self.assertEqual(filepath_prompt.status["answered"], True)
            self.assertEqual(filepath_prompt.status["result"], "./file1")

    def test_default_answer(self):
        with create_pipe_input() as inp:
            inp.send_text("\n")
            filepath_prompt = FilePathPrompt(
                message="hello",
                style=InquirerPyStyle({"qmark": "bold"}),
                default=".vim",
                input=inp,
                output=DummyOutput(),
            )
            result = filepath_prompt.execute()
            self.assertEqual(result, ".vim")
            self.assertEqual(filepath_prompt.status["answered"], True)
            self.assertEqual(filepath_prompt.status["result"], ".vim")

    @patch.object(Buffer, "validate_and_handle")
    def test_validation(self, mocked_validate):
        def _hello():
            filepath_prompt._session.app.exit(result="hello")

        with create_pipe_input() as inp:
            mocked_validate.side_effect = _hello
            inp.send_text("hello\n")
            filepath_prompt = FilePathPrompt(
                message="fooboo",
                style=InquirerPyStyle({"qmark": ""}),
                default=".vim",
                validate=PathValidator(),
                input=inp,
                output=DummyOutput(),
            )
            result = filepath_prompt.execute()
            mocked_validate.assert_called_once()
            self.assertEqual(result, "hello")
            self.assertEqual(filepath_prompt.status["answered"], False)
            self.assertEqual(filepath_prompt.status["result"], None)

    def test_get_prompt_message(self):
        filepath_prompt = FilePathPrompt(
            message="brah", style=InquirerPyStyle({"foo": ""}), qmark="!", amark="x"
        )
        message = filepath_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "!"),
                ("class:question", " brah"),
                ("class:instruction", " "),
            ],
        )

        filepath_prompt.status["answered"] = True
        filepath_prompt.status["result"] = "hello"
        message = filepath_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "x"),
                ("class:answered_question", " brah"),
                ("class:answer", " hello"),
            ],
        )

    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.filepath.FilePathPrompt._get_prompt_message")
    @patch("InquirerPy.base.simple.Style.from_dict")
    @patch("InquirerPy.base.simple.KeyBindings")
    @patch("InquirerPy.prompts.input.PromptSession")
    def test_callable_called(
        self,
        MockedSession,
        MockedKeyBindings,
        MockedStyle,
        mocked_message,
        MockedLexer,
    ):
        def _validation(_):
            return True

        FilePathPrompt(
            message="yes",
            style=InquirerPyStyle({"yes": ""}),
            default="",
            qmark="XD",
            multicolumn_complete=True,
            validate=_validation,
            vi_mode=True,
            only_directories=True,
        )
        kb = MockedKeyBindings()
        style = MockedStyle()
        lexer = MockedLexer()
        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            completer=ANY,
            validator=ANY,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.VI,
            lexer=lexer,
            is_password=False,
            multiline=False,
            complete_style=CompleteStyle.MULTI_COLUMN,
            wrap_lines=True,
            bottom_toolbar=None,
        )

        MockedStyle.assert_has_calls([call({"yes": ""})])

    def test_invalid_argument(self):
        self.assertRaises(InvalidArgument, FilePathPrompt, "hello", None, False, 12)
        FilePathPrompt(message="hello", default=lambda _: "12")

    @patch("os.name")
    def test_completer_explicit_currdir_all_win(self, mocked_platform):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = ".\\"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(
                sorted(completions),
                sorted(self.dirs_to_create + self.files_to_create),
            )

    @patch("os.name")
    def test_completer_currdir_file_win(self, mocked_platform):
        with self.chdir(self.test_dir):
            completer = FilePathCompleter()
            doc_text = ".\\file"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), ["file1", "file2", "file3"])
