import os
import unittest
from contextlib import contextmanager
from pathlib import Path

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
            validator = PathValidator(is_file=True)
            self.execute_success_case(validator, "test_PathValidator")
            validator = PathValidator(is_dir=True)
            self.assertRaises(ValidationError, validator.validate, self.document)
            self.document._text = "prompts"
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

    def test_numberValidator(self):
        self.document._text = "asfasdf"
        validator = NumberValidator()
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "12"
        self.execute_success_case(validator, "test_numberValidator")
        self.document._text = "1.2"
        validator = NumberValidator(float_allowed=False)
        self.assertRaises(ValidationError, validator.validate, self.document)
        validator = NumberValidator(float_allowed=True)
        self.execute_success_case(validator, "test_numberValidator")

    def test_dateValidator(self):
        validator = DateValidator()
        self.document._text = "2042-04-02"
        self.execute_success_case(validator, "test_dateValidator")
        self.document._text = "0001-12-12"
        self.execute_success_case(validator, "test_dateValidator")
        self.document._text = "11-12-11"
        self.assertRaises(ValidationError, validator.validate, self.document)
        self.document._text = "1212-12-12 12:12:12"
        self.execute_success_case(validator, "test_dateValidator")
        self.document._text = "1212-12-12T12:12:12"
        self.execute_success_case(validator, "test_dateValidator")
        self.document._text = "2023-02-29"
        self.assertRaises(ValidationError, validator.validate, self.document)
        validator = DateValidator(formats=["%d/%m/%Y"])
        self.document._text = "28/02/2023"
        self.execute_success_case(validator, "test_dateValidator")