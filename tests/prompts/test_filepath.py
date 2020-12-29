from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.filepath import FilePathCompleter
from InquirerPy.validator import PathValidator


class TestFilePath(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()
        self.dirs_to_create = ["dir1", "dir2", "dir3", ".dir"]
        self.files_to_create = ["file1", "file2", "file3", ".file"]
        self.test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files()

    def tearDown(self):
        self.inp.close()
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

    def test_input(self):
        self.inp.send_text("./file1\n")
        filepath_prompt = FilePathPrompt(
            message="hello",
            style={"qmark": "bold"},
            input=self.inp,
            output=DummyOutput(),
        )
        result = filepath_prompt.execute()
        self.assertEqual(result, "./file1")
        self.assertEqual(filepath_prompt.status["answered"], True)
        self.assertEqual(filepath_prompt.status["result"], "./file1")

    def test_default_answer(self):
        self.inp.send_text("\n")
        filepath_prompt = FilePathPrompt(
            message="hello",
            style={"qmark": "bold"},
            default=".vim",
            input=self.inp,
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

        mocked_validate.side_effect = _hello
        self.inp.send_text("hello\n")
        filepath_prompt = FilePathPrompt(
            message="fooboo",
            style={"qmark": ""},
            default=".vim",
            validate=PathValidator(),
            input=self.inp,
            output=DummyOutput(),
        )
        result = filepath_prompt.execute()
        mocked_validate.assert_called_once()
        self.assertEqual(result, "hello")
        self.assertEqual(filepath_prompt.status["answered"], False)
        self.assertEqual(filepath_prompt.status["result"], None)

    def test_get_prompt_message(self):
        filepath_prompt = FilePathPrompt(message="brah", style={"foo": ""}, qmark="!")
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
                ("class:questionmark", "!"),
                ("class:question", " brah"),
                ("class:answer", " hello"),
            ],
        )

    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.filepath.Validator.from_callable")
    @patch("InquirerPy.prompts.filepath.FilePathPrompt._get_prompt_message")
    @patch("InquirerPy.base.Style.from_dict")
    @patch("InquirerPy.base.KeyBindings")
    @patch("InquirerPy.prompts.input.PromptSession")
    def test_callable_called(
        self,
        MockedSession,
        MockedKeyBindings,
        MockedStyle,
        mocked_message,
        mocked_validator,
        MockedLexer,
    ):
        def _validation(_):
            return True

        FilePathPrompt(
            message="yes",
            style={"yes": ""},
            default="",
            qmark="XD",
            validate=_validation,
            editing_mode="vim",
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
            validator=mocked_validator(),
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.VI,
            lexer=lexer,
            is_password=False,
            multiline=False,
        )

        MockedStyle.assert_has_calls([call({"yes": ""})])
        mocked_validator.assert_has_calls(
            [call(_validation, "Invalid input", move_cursor_to_end=True)]
        )
        MockedLexer.assert_has_calls([call("class:input")])
