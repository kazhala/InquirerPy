import os
import unittest
from unittest.mock import ANY, PropertyMock, call, patch

from prompt_toolkit.shortcuts.prompt import PromptSession

from InquirerPy.base import BaseComplexPrompt
from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts import FuzzyPrompt
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.prompts.expand import ExpandPrompt
from InquirerPy.prompts.filepath import FilePathPrompt
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.prompts.list import ListPrompt
from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.resolver import prompt
from InquirerPy.utils import InquirerPyStyle

from .style import get_sample_style


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
        self.assertEqual(result, {0: True})

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
            style=InquirerPyStyle(get_sample_style()),
            vi_mode=False,
            session_result=ANY,
        )
        mocked_confirm_execute.assert_called_once()
        self.assertEqual(result, {0: False})

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
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    session_result=ANY,
                ),
                call(
                    message="world",
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    session_result=ANY,
                ),
            ]
        )
        mocked_filepath_init.assert_has_calls(
            [
                call(
                    message="whaat",
                    style=InquirerPyStyle(get_sample_style()),
                    default="./",
                    vi_mode=False,
                    session_result=ANY,
                )
            ]
        )
        mocked_confirm_execute.assert_has_calls(
            [call(raise_keyboard_interrupt=True), call(raise_keyboard_interrupt=True)]
        )
        self.assertEqual(result, {0: False, "foo": False, "boo": "hello.py"})

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
        os.environ["INQUIRERPY_VI_MODE"] = "true"

        questions = [{"type": "confirm", "message": "Confirm?", "name": "question1"}]
        result = prompt(questions)
        mocked_confirm_execute.assert_called_once()
        mocked_confirm_init.assert_called_once_with(
            message="Confirm?",
            style=InquirerPyStyle(get_sample_style()),
            vi_mode=False,
            session_result={"question1": False},
        )
        self.assertEqual(result, {"question1": False})
        del os.environ["INQUIRERPY_VI_MODE"]

        mocked_secret_init.return_value = None
        mocked_secret_execute.return_value = "111111"
        mocked_confirm_execute.reset_mock()
        mocked_confirm_init.reset_mock()
        mocked_confirm_execute.return_value = True
        questions = [
            {"type": "confirm", "message": "Confirm?", "name": "10"},
            {"type": "confirm", "message": "What?"},
            {"type": "password", "message": "haha"},
        ]
        result = prompt(
            questions, style={"qmark": "#ffffff"}, vi_mode=True, style_override=False
        )
        mocked_confirm_execute.assert_has_calls(
            [call(raise_keyboard_interrupt=True), call(raise_keyboard_interrupt=True)]
        )
        mocked_confirm_init.assert_has_calls(
            [
                call(
                    message="Confirm?",
                    style=InquirerPyStyle(get_sample_style({"qmark": "#ffffff"})),
                    vi_mode=True,
                    session_result=ANY,
                ),
                call(
                    message="What?",
                    style=InquirerPyStyle(get_sample_style({"qmark": "#ffffff"})),
                    vi_mode=True,
                    session_result=ANY,
                ),
            ]
        )
        mocked_secret_init.reset_mock()
        questions = [
            {"type": "confirm", "message": "Confirm?", "name": "10"},
            {"type": "confirm", "message": "What?"},
            {"type": "password", "message": "haha"},
        ]
        result = prompt(
            questions,
            style={"qmark": "#ffffff"},
            vi_mode=True,
            style_override=True,
        )
        style = get_sample_style()
        for key in style.keys():
            style[key] = ""
        style["qmark"] = "#ffffff"
        style["fuzzy_border"] = style.pop("frame.border")
        mocked_secret_init.assert_has_calls(
            [
                call(
                    message="haha",
                    style=InquirerPyStyle(style),
                    vi_mode=True,
                    session_result={"10": True, 1: True, 2: "111111"},
                )
            ]
        )
        self.assertEqual(result, {"10": True, 1: True, 2: "111111"})

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
        mocked_execute.assert_has_calls(
            [call(raise_keyboard_interrupt=True), call(raise_keyboard_interrupt=True)]
        )
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    default=True,
                    session_result=ANY,
                ),
                call(
                    message="Confirm second?",
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    session_result=ANY,
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
        mocked_execute.assert_has_calls(
            [call(raise_keyboard_interrupt=True), call(raise_keyboard_interrupt=True)]
        )
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    default=True,
                    session_result=ANY,
                ),
                call(
                    message="Confirm?",
                    style=InquirerPyStyle(get_sample_style()),
                    vi_mode=False,
                    session_result=ANY,
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
                ("class:answermark", "?"),
                ("class:answered_question", " Select one"),
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
                ("class:answermark", "?"),
                ("class:answered_question", " Select one"),
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
                ("class:answermark", "?"),
                ("class:answered_question", " Select one"),
                ("class:answer", " 22"),
            ],
        )

    @patch.object(PromptSession, "prompt")
    def test_optional_keyboard_interrupt(self, mocked_execute):
        mocked_execute.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        questions = [{"type": "input", "message": "hello"}]
        result = prompt(questions, raise_keyboard_interrupt=False)
        self.assertEqual(result, {0: None})

        mocked_execute.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        self.assertRaises(
            KeyboardInterrupt, prompt, questions, raise_keyboard_interrupt=True
        )

        input_prompt = InputPrompt(message="hello")
        input_prompt.status = {
            "answered": True,
            "result": INQUIRERPY_KEYBOARD_INTERRUPT,
        }
        self.assertEqual(
            input_prompt._get_prompt_message(),
            [("class:skipped", "?"), ("class:skipped", " hello ")],
        )

        os.environ["INQUIRERPY_NO_RAISE_KBI"] = "true"
        result = prompt(questions)
        self.assertEqual(result, {0: None})

        os.environ["INQUIRERPY_NO_RAISE_KBI"] = "true"
        result = prompt(questions, raise_keyboard_interrupt=True)
        self.assertEqual(result, {0: None})

    @patch.object(ListPrompt, "execute")
    @patch.object(InputPrompt, "execute")
    @patch.object(BaseComplexPrompt, "kb_maps", new_callable=PropertyMock)
    def test_custom_kb(self, mocked_kb, mocked_execute1, mocked_execute2):
        questions = [{"type": "input", "message": "hello"}]
        prompt(questions, keybindings={"up": [{"key": "up"}]})
        mocked_kb.assert_not_called()
        questions = [{"type": "list", "message": "aasdf", "choices": [1, 2, 3]}]
        prompt(questions, keybindings={"up": [{"key": "c-p"}]}, vi_mode=True)
        mocked_kb.assert_has_calls(
            [
                call(
                    {
                        "down": ANY,
                        "up": [{"key": "c-p"}],
                        "toggle": ANY,
                        "toggle-down": ANY,
                        "toggle-up": ANY,
                        "toggle-all": ANY,
                        "toggle-all-true": ANY,
                        "toggle-all-false": ANY,
                    }
                )
            ]
        )
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
        prompt(questions, keybindings={"up": [{"key": "c-p"}]}, vi_mode=True)
        mocked_kb.assert_has_calls(
            [
                call(
                    {
                        "down": ANY,
                        "up": [{"key": "c-w"}],
                        "toggle": ANY,
                        "toggle-down": ANY,
                        "toggle-up": ANY,
                        "toggle-all": ANY,
                        "toggle-all-true": ANY,
                        "toggle-all-false": ANY,
                    }
                )
            ]
        )
        try:
            mocked_kb.assert_has_calls([call("c-p", filter=ANY)])
            self.fail("should not have called")
        except:
            pass

    @patch.object(FuzzyPrompt, "__init__")
    @patch.object(FuzzyPrompt, "execute")
    def test_resolver_when_not_poped(self, mocked_execute, mocked_init):
        mocked_init.return_value = None
        mocked_execute.return_value = 1
        questions = [
            {"message": "", "choices": [1, 2, 3], "type": "fuzzy"},
            {
                "message": "",
                "type": "fuzzy",
                "choices": [4, 5, 6],
                "when": lambda result: result == 1,
            },
        ]
        prompt(questions)

    @patch.object(InputPrompt, "execute")
    def test_single_dict_question(self, mocked_execute):
        mocked_execute.return_value = None
        prompt({"type": "input", "message": "Name:"})
