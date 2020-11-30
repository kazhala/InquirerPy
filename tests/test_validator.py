from contextlib import contextmanager
import os
from pathlib import Path
import unittest

from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError

from InquirerPy.validator import *


class TestValidators(unittest.TestCase):
    def setUp(self):
        self.document = Document()

    @contextmanager
    def chdir(self, directory):
        orig_dir = os.getcwd()
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(orig_dir)

    def execute_success_case(self, validator, name: str):
        try:
            validator.validate(self.document)
        except ValidationError:
            self.fail("%s raised Exception when input is valid" % name)

    def test_PathValidator(self):
        self.document._text = "asfasfd"
        validator = PathValidator()
        file_dir = Path(__file__).resolve().parent
        with self.chdir(file_dir):
            self.assertRaises(ValidationError, validator.validate, self.document)

            self.document._text = "test_validator.py"
            self.execute_success_case(validator, "test_PathValidator")

    def test_EmptyInputValidator(self):
        self.document._text = ""
        validator = EmptyInputValidator()
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "asdfa"
        self.execute_success_case(validator, "test_EmptyInputValidator")

    def test_PasswordValidator(self):
        self.document._text = "fasfasfads"
        validator = PasswordValidator(length=8, cap=True, special=True, number=True)
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "!iiasdfasfafdsfad99"
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "!Iiasdfasfafdsfad"
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "!Iiasdfasfafdsfad99"
        self.execute_success_case(validator, "test_PasswordValidator")