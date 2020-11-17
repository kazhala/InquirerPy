from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.filepath import FilePath
from InquirerPy.prompts.filepath import FilePathCompleter


class TestFilePath(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()
        self.dirs_to_create = ["dir1", "dir2", "dir3", ".dir"]
        self.files_to_create = ["file1", "file2", "file3", ".file"]

    def tearDown(self):
        self.inp.close()

    @contextmanager
    def chdir(self, directory):
        orig_dir = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(orig_dir)

    def create_temp_files(self, test_dir):
        for directory in self.dirs_to_create:
            test_dir.joinpath(directory).mkdir(exist_ok=True)
        for file in self.files_to_create:
            with test_dir.joinpath(file).open("wb") as output_file:
                output_file.write("".encode("UTF-8"))

    def test_completer_explicit_currdir_all(self):
        test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files(test_dir)

        with self.chdir(test_dir):
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

        shutil.rmtree(test_dir)

    def test_completer_currdir_file(self):
        test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files(test_dir)

        with self.chdir(test_dir):
            completer = FilePathCompleter()
            doc_text = "./file"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), ["file1", "file2", "file3"])

        shutil.rmtree(test_dir)

    def test_completer_hidden(self):
        test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files(test_dir)

        with self.chdir(test_dir):
            completer = FilePathCompleter()
            doc_text = "."
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), [".dir", ".file"])

        shutil.rmtree(test_dir)

    def test_completer_normal(self):
        test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files(test_dir)

        with self.chdir(test_dir):
            completer = FilePathCompleter()
            doc_text = "dir"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertEqual(sorted(completions), ["dir1", "dir2", "dir3"])

        shutil.rmtree(test_dir)

    def test_completer_expanduser(self):
        test_dir = Path(tempfile.mkdtemp())
        self.create_temp_files(test_dir)

        with self.chdir(test_dir):
            completer = FilePathCompleter()
            doc_text = "~/"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))
            ]
            self.assertGreater(len(completions), 0)

        shutil.rmtree(test_dir)
