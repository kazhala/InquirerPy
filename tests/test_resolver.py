import os
import unittest
from unittest.mock import ANY, call, patch

from InquirerPy.base import BaseComplexPrompt
from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.prompts.expand import ExpandPrompt
from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.resolver import prompt

style = {
    "questionmark": "#e5c07b",
    "answer": "#61afef",
    "input": "#98c379",
    "question": "",
    "instruction": "",
    "pointer": "#61afef",
    "checkbox": "#98c379",
    "separator": "",
    "skipped": "#5c6370",
    "fuzzy_prompt": "#c678dd",
    "fuzzy_info": "#98c379",
    "marker": "#e5c07b",
    "frame.border": "#4b5263",
    "fuzzy_match": "#c678dd",
    "validator": "",
}


class TestResolver(unittest.TestCase):
    @patch("InquirerPy.resolver.ConfirmPrompt.execute")
    def test_exceptions(self, mocked_confirm):
        questions = "hello"
        self.assertRaises(InvalidArgument, prompt, questions)

        questions = [{"name": "hello"}]
        self.assertRaises(RequiredKeyNotFound, prompt, questions)

        questions = [{"type": "confirm"}]
        self.assertRaises(RequiredKeyNotFound, prompt, questions)

        questions = [{"type": "confirm", "message": "hello"}]
        mocked_confirm.return_value = True
        result = prompt(questions)
        mocked_confirm.assert_called_once()
        self.assertEqual(result, {"0": True})

    @patch.object(FilePathPrompt, "__init__")
    @patch.object(FilePathPrompt, "execute")
    @patch.object(ConfirmPrompt, "__init__")
    @patch.object(ConfirmPrompt, "execute")
    def test_resolver_normal(
        self,
        mocked_confirm_execute,
        mocked_confirm_init,
        mocked_filepath_execute,
        mocked_filepath_init,
    ):
        mocked_confirm_init.return_value = None
        mocked_confirm_execute.return_value = False
        questions = [
            {"type": "confirm", "message": "hello"},
        ]
        result = prompt(questions)
        mocked_confirm_init.assert_called_once_with(
            message="hello",
            style=style,
            editing_mode="default",
        )
        mocked_confirm_execute.assert_called_once()
        self.assertEqual(result, {"0": False})

        mocked_filepath_init.return_value = None
        mocked_filepath_execute.return_value = "hello.py"
        mocked_confirm_init.reset_mock()
        mocked_confirm_execute.reset_mock()
        questions = [
            {"type": "confirm", "message": "hello"},
            {"type": "confirm", "message": "world", "name": "foo"},
            {"type": "filepath", "message": "whaat", "name": "boo", "default": "./"},
        ]
        result = prompt(questions)
        mocked_confirm_init.assert_has_calls(
            [
                call(
                    message="hello",
                    style=style,
                    editing_mode="default",
                ),
                call(
                    message="world",
                    style=style,
                    editing_mode="default",
                ),
            ]
        )
        mocked_filepath_init.assert_has_calls(
            [
                call(
                    message="whaat",
                    style=style,
                    default="./",
                    editing_mode="default",
                )
            ]
        )
        mocked_confirm_execute.assert_has_calls([call(), call()])
        self.assertEqual(result, {"0": False, "foo": False, "boo": "hello.py"})

    @patch.object(SecretPrompt, "__init__")
    @patch.object(SecretPrompt, "execute")
    @patch.object(ConfirmPrompt, "__init__")
    @patch.object(ConfirmPrompt, "execute")
    def test_resolver_style_keys(
        self,
        mocked_confirm_execute,
        mocked_confirm_init,
        mocked_secret_execute,
        mocked_secret_init,
    ):
        mocked_confirm_execute.return_value = False
        mocked_confirm_init.return_value = None
        os.environ["INQUIRERPY_EDITING_MODE"] = "emacs"

        questions = [{"type": "confirm", "message": "Confirm?", "name": "question1"}]
        result = prompt(questions)
        mocked_confirm_execute.assert_called_once()
        mocked_confirm_init.assert_called_once_with(
            message="Confirm?",
            style=style,
            editing_mode="emacs",
        )
        self.assertEqual(result, {"question1": False})
        del os.environ["INQUIRERPY_EDITING_MODE"]

        mocked_secret_init.return_value = None
        mocked_secret_execute.return_value = "111111"
        mocked_confirm_execute.reset_mock()
        mocked_confirm_init.reset_mock()
        mocked_confirm_execute.return_value = True
        questions = [
            {"type": "confirm", "message": "Confirm?", "name": "10"},
            {"type": "confirm", "message": "What?"},
            {"type": "secret", "message": "haha"},
        ]
        result = prompt(questions, style={"qmark": "#ffffff"}, editing_mode="vim")
        mocked_confirm_execute.assert_has_calls([call(), call()])
        mocked_confirm_init.assert_has_calls(
            [
                call(
                    message="Confirm?",
                    style={
                        "questionmark": "#e5c07b",
                        "answer": "#61afef",
                        "input": "#98c379",
                        "question": "",
                        "instruction": "",
                        "pointer": "#61afef",
                        "checkbox": "#98c379",
                        "separator": "",
                        "skipped": "#5c6370",
                        "validator": "",
                        "marker": "#e5c07b",
                        "fuzzy_prompt": "#c678dd",
                        "fuzzy_info": "#98c379",
                        "fuzzy_match": "#c678dd",
                        "qmark": "#ffffff",
                        "frame.border": "#4b5263",
                    },
                    editing_mode="vim",
                ),
                call(
                    message="What?",
                    style={
                        "questionmark": "#e5c07b",
                        "answer": "#61afef",
                        "input": "#98c379",
                        "question": "",
                        "instruction": "",
                        "pointer": "#61afef",
                        "checkbox": "#98c379",
                        "separator": "",
                        "skipped": "#5c6370",
                        "validator": "",
                        "marker": "#e5c07b",
                        "fuzzy_prompt": "#c678dd",
                        "fuzzy_info": "#98c379",
                        "fuzzy_match": "#c678dd",
                        "qmark": "#ffffff",
                        "frame.border": "#4b5263",
                    },
                    editing_mode="vim",
                ),
            ]
        )
        mocked_secret_init.reset_mock()
        questions = [
            {"type": "confirm", "message": "Confirm?", "name": "10"},
            {"type": "confirm", "message": "What?"},
            {"type": "secret", "message": "haha"},
        ]
        result = prompt(
            questions,
            style={"qmark": "#ffffff"},
            editing_mode="vim",
            style_override=True,
        )
        mocked_secret_init.assert_has_calls(
            [call(message="haha", style={"qmark": "#ffffff"}, editing_mode="vim")]
        )
        self.assertEqual(result, {"10": True, "1": True, "2": "111111"})

    @patch.object(ConfirmPrompt, "__init__")
    @patch.object(ConfirmPrompt, "execute")
    def test_resolver_condition(self, mocked_execute, mocked_init):
        mocked_init.return_value = None
        mocked_execute.return_value = True
        questions = [
            {
                "type": "confirm",
                "name": "first",
                "message": "Confirm first?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "second",
                "message": "Confirm second?",
                "when": lambda result: result["first"] == True,
            },
            {
                "type": "confirm",
                "name": "third",
                "message": "Confirm?",
                "when": lambda result: result["second"] == False,
            },
        ]
        result = prompt(questions)
        mocked_execute.assert_has_calls([call(), call()])
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style=style,
                    editing_mode="default",
                    default=True,
                ),
                call(
                    message="Confirm second?",
                    style=style,
                    editing_mode="default",
                    when=ANY,
                ),
            ]
        )
        self.assertEqual(result, {"first": True, "second": True, "third": None})

        mocked_init.reset_mock()
        mocked_execute.reset_mock()
        questions = [
            {
                "type": "confirm",
                "name": "first",
                "message": "Confirm first?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "second",
                "message": "Confirm second?",
                "when": lambda result: result["first"] == False,
            },
            {
                "type": "confirm",
                "name": "third",
                "message": "Confirm?",
                "when": lambda result: result["second"] == None,
            },
        ]
        result = prompt(questions)
        mocked_execute.assert_has_calls([call(), call()])
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style=style,
                    editing_mode="default",
                    default=True,
                ),
                call(
                    message="Confirm?",
                    style=style,
                    editing_mode="default",
                    when=ANY,
                ),
            ]
        )
        self.assertEqual(result, {"first": True, "second": None, "third": True})

    @patch.object(ExpandPrompt, "execute")
    def test_resolver_filter(self, mocked_execute):
        mocked_execute.return_value = "boo"
        prompt = ExpandPrompt(
            message="Select one",
            choices=[
                {"name": "foo", "value": "boo", "key": "f"},
                {"name": "hello", "value": "world", "key": "w"},
            ],
            filter=lambda x: 2 * x,
        )
        result = prompt._filter(prompt.execute())
        self.assertEqual(result, "booboo")

    def test_resolver_transformer(self):
        prompt = ListPrompt(
            message="Select one", choices=["1", "2", "3"], transformer=lambda x: x * 2
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one"),
                ("class:instruction", " "),
            ],
        )
        prompt.status["result"] = "1"
        prompt.status["answered"] = True
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one"),
                ("class:answer", " 11"),
            ],
        )

        prompt = InputPrompt(
            message="Select one",
            transformer=lambda x: x * 2,
        )
        prompt.status["result"] = "2"
        prompt.status["answered"] = True
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one"),
                ("class:answer", " 22"),
            ],
        )

        prompt = SecretPrompt(
            message="Select one",
            transformer=lambda x: x * 2,
        )
        prompt.status["result"] = "2"
        prompt.status["answered"] = True
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one"),
                ("class:answer", " 22"),
            ],
        )

    @patch.object(InputPrompt, "execute")
    def test_optional_keyboard_interrupt(self, mocked_execute):
        mocked_execute.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        questions = [{"type": "input", "message": "hello"}]
        result = prompt(questions, raise_keyboard_interrupt=False)
        self.assertEqual(result, {"0": None})

        input_prompt = InputPrompt(message="")
        input_prompt.status = {
            "answered": True,
            "result": INQUIRERPY_KEYBOARD_INTERRUPT,
        }
        self.assertEqual(input_prompt._get_prompt_message(), [("class:skipped", "?  ")])

    @patch.object(ListPrompt, "execute")
    @patch.object(InputPrompt, "execute")
    @patch.object(BaseComplexPrompt, "_register_kb")
    def test_custom_kb(self, mocked_kb, mocked_execute1, mocked_execute2):
        questions = [{"type": "input", "message": "hello"}]
        prompt(questions, keybindings={"up": [{"key": "up"}]})
        mocked_kb.assert_not_called()
        questions = [{"type": "list", "message": "aasdf", "choices": [1, 2, 3]}]
        prompt(questions, keybindings={"up": [{"key": "c-p"}]}, editing_mode="vim")
        mocked_kb.assert_has_calls([call("c-p", filter=True)])
        try:
            mocked_kb.assert_has_calls([call("k", filter=ANY)])
            self.fail("should not have called")
        except:
            pass

        mocked_kb.reset_mock()
        questions = [
            {
                "type": "list",
                "message": "aasdf",
                "choices": [1, 2, 3],
                "keybindings": {"up": [{"key": "c-w"}]},
            }
        ]
        prompt(questions, keybindings={"up": [{"key": "c-p"}]}, editing_mode="vim")
        mocked_kb.assert_has_calls([call("c-w", filter=True)])
        try:
            mocked_kb.assert_has_calls([call("c-p", filter=ANY)])
            self.fail("should not have called")
        except:
            pass
