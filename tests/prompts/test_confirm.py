import unittest
from unittest.mock import ANY, patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.keys import Keys
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.confirm import Confirm


class TestConfirmPrompt(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_default_false(self):
        self.inp.send_text("\n")
        confirm_prompt = Confirm(
            message="hello",
            style={"symbol": "bold"},
            default_true=False,
            symbol="x",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], False)

    def test_default_true(self):
        self.inp.send_text("\n")
        confirm_prompt = Confirm(
            message="hello",
            style={"symbol": "bold", "answer": "#000000"},
            default_true=True,
            symbol="x",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, True)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], True)

    def test_input_y(self):
        self.inp.send_text("y")
        confirm_prompt = Confirm(
            message="hello",
            style={},
            default_true=True,
            symbol="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.session.prompt()
        self.assertEqual(result, True)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], True)

        self.inp.send_text("Y")
        confirm_prompt = Confirm(
            message="hello",
            style={},
            default_true=True,
            symbol="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, True)

    def test_input_n(self):
        self.inp.send_text("n")
        confirm_prompt = Confirm(
            message="hello",
            style={},
            default_true=True,
            symbol="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], False)

        self.inp.send_text("N")
        confirm_prompt = Confirm(
            message="hello",
            style={},
            default_true=True,
            symbol="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)

    def test_get_prompt_message(self):
        confirm_prompt = Confirm(
            message="hello",
            style={},
            default_true=True,
            symbol="?",
        )
        message = confirm_prompt.get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "?"),
                ("class:question", " hello "),
                ("class:instruction", " (Y/n)"),
            ],
        )

        confirm_prompt.status["answered"] = True
        confirm_prompt.status["result"] = True
        message = confirm_prompt.get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "?"),
                ("class:question", " hello "),
                ("class:answer", " Yes"),
            ],
        )

        confirm_prompt = Confirm(
            message="Are you sure?",
            style={},
            default_true=False,
            symbol="x",
        )
        message = confirm_prompt.get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "x"),
                ("class:question", " Are you sure? "),
                ("class:instruction", " (y/N)"),
            ],
        )

        confirm_prompt.status["answered"] = True
        confirm_prompt.status["result"] = False
        message = confirm_prompt.get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "x"),
                ("class:question", " Are you sure? "),
                ("class:answer", " No"),
            ],
        )

    @patch("InquirerPy.prompts.confirm.Confirm.get_prompt_message")
    @patch("InquirerPy.prompts.confirm.Style.from_dict")
    @patch("InquirerPy.prompts.confirm.KeyBindings")
    @patch("InquirerPy.prompts.confirm.PromptSession")
    def test_callable_called(
        self, MockedSession, MockedKeyBindings, MockedStyle, mocked_message
    ):
        prompt = Confirm(
            message="Are you sure?",
            style={},
            default_true=False,
            symbol="x",
        )
        kb = MockedKeyBindings()
        style = MockedStyle()
        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            input=None,
            output=None,
        )
