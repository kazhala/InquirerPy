import os
import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.exceptions import InvalidArgumentType, RequiredKeyNotFound
from InquirerPy.prompts.confirm import Confirm
from InquirerPy.resolver import prompt


class TestResolver(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    @patch("InquirerPy.resolver.Confirm.execute")
    def test_exceptions(self, mocked_confirm):
        questions = "hello"
        self.assertRaises(InvalidArgumentType, prompt, questions)

        questions = [{"name": "hello"}]
        self.assertRaises(RequiredKeyNotFound, prompt, questions)

        questions = [{"type": "confirm"}]
        self.assertRaises(RequiredKeyNotFound, prompt, questions)

        questions = [{"type": "confirm", "question": "hello"}]
        mocked_confirm.return_value = True
        result = prompt(questions)
        mocked_confirm.assert_called_once()
        self.assertEqual(result, {"0": True})

    @patch.object(Confirm, "__init__")
    @patch.object(Confirm, "execute")
    def test_resolver_normal(self, mocked_execute, mocked_init):
        mocked_init.return_value = None
        mocked_execute.return_value = False
        questions = [
            {"type": "confirm", "question": "hello"},
        ]
        result = prompt(questions)
        mocked_init.assert_called_once_with(
            message="hello",
            style={
                "symbol": "#ffcb04",
                "answer": "#61afef",
                "question": "",
                "instruction": "",
            },
            key_binding_mode="default",
        )
        mocked_execute.assert_called_once()
        self.assertEqual(result, {"0": False})

        mocked_init.reset_mock()
        mocked_execute.reset_mock()
        questions = [
            {"type": "confirm", "question": "hello"},
            {"type": "confirm", "question": "world", "name": "foo"},
        ]
        result = prompt(questions)
        mocked_init.assert_has_calls(
            [
                call(
                    message="hello",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                ),
                call(
                    message="world",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                ),
            ]
        )
        mocked_execute.assert_has_calls([call(), call()])
        self.assertEqual(result, {"0": False, "foo": False})

    @patch.object(Confirm, "__init__")
    @patch.object(Confirm, "execute")
    def test_resolver_style_keys(self, mocked_execute, mocked_init):
        mocked_execute.return_value = False
        mocked_init.return_value = None
        os.environ["INQUIRERPY_STYLE_SYMBOL"] = "#000000"
        os.environ["INQUIRERPY_STYLE_ANSWER"] = "#111111"
        os.environ["INQUIRERPY_STYLE_QUESTION"] = "#222222"
        os.environ["INQUIRERPY_STYLE_INSTRUCTION"] = "#333333"
        os.environ["INQUIRERPY_KEYBINDING_MODE"] = "emacs"

        questions = [{"type": "confirm", "question": "Confirm?", "name": "question1"}]
        result = prompt(questions)
        mocked_execute.assert_called_once()
        mocked_init.assert_called_once_with(
            message="Confirm?",
            style={
                "symbol": "#000000",
                "answer": "#111111",
                "question": "#222222",
                "instruction": "#333333",
            },
            key_binding_mode="emacs",
        )
        self.assertEqual(result, {"question1": False})
        del os.environ["INQUIRERPY_STYLE_SYMBOL"]
        del os.environ["INQUIRERPY_STYLE_ANSWER"]
        del os.environ["INQUIRERPY_STYLE_QUESTION"]
        del os.environ["INQUIRERPY_STYLE_INSTRUCTION"]
        del os.environ["INQUIRERPY_KEYBINDING_MODE"]

        mocked_execute.reset_mock()
        mocked_init.reset_mock()
        mocked_execute.return_value = True
        questions = [
            {"type": "confirm", "question": "Confirm?", "name": "10"},
            {"type": "confirm", "question": "What?"},
        ]
        result = prompt(questions, style={"symbol": "#ffffff"}, key_binding_mode="vim")
        mocked_execute.assert_has_calls([call(), call()])
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm?",
                    style={
                        "symbol": "#ffffff",
                    },
                    key_binding_mode="vim",
                ),
                call(
                    message="What?",
                    style={
                        "symbol": "#ffffff",
                    },
                    key_binding_mode="vim",
                ),
            ]
        )
        self.assertEqual(result, {"10": True, "1": True})

    @patch.object(Confirm, "__init__")
    @patch.object(Confirm, "execute")
    def test_resolver_condition(self, mocked_execute, mocked_init):
        mocked_init.return_value = None
        mocked_execute.return_value = True
        questions = [
            {
                "type": "confirm",
                "name": "first",
                "question": "Confirm first?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "second",
                "question": "Confirm second?",
                "condition": lambda result: result["first"] == True,
            },
            {
                "type": "confirm",
                "name": "third",
                "question": "Confirm?",
                "condition": lambda result: result["second"] == False,
            },
        ]
        result = prompt(questions)
        mocked_execute.assert_has_calls([call(), call()])
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                    default=True,
                ),
                call(
                    message="Confirm second?",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                    condition=ANY,
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
                "question": "Confirm first?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "second",
                "question": "Confirm second?",
                "condition": lambda result: result["first"] == False,
            },
            {
                "type": "confirm",
                "name": "third",
                "question": "Confirm?",
                "condition": lambda result: result["second"] == None,
            },
        ]
        result = prompt(questions)
        mocked_execute.assert_has_calls([call(), call()])
        mocked_init.assert_has_calls(
            [
                call(
                    message="Confirm first?",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                    default=True,
                ),
                call(
                    message="Confirm?",
                    style={
                        "symbol": "#ffcb04",
                        "answer": "#61afef",
                        "question": "",
                        "instruction": "",
                    },
                    key_binding_mode="default",
                    condition=ANY,
                ),
            ]
        )
        self.assertEqual(result, {"first": True, "second": None, "third": True})
