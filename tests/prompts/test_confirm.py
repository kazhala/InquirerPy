import unittest
from unittest.mock import patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts.prompt import PromptSession

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.prompts.confirm import ConfirmPrompt
from InquirerPy.utils import InquirerPyStyle


class TestConfirmPrompt(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_default_false(self):
        self.inp.send_text("\n")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=InquirerPyStyle({"qmark": "bold"}),
            default=False,
            qmark="x",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], False)

    def test_default_true(self):
        self.inp.send_text("\n")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=InquirerPyStyle({"qmark": "bold", "answer": "#000000"}),
            default=True,
            qmark="x",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, True)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], True)

    def test_input_y(self):
        self.inp.send_text("y")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt._session.prompt()
        self.assertEqual(result, True)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], True)

        self.inp.send_text("Y")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, True)

    def test_input_n(self):
        self.inp.send_text("n")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], False)

        self.inp.send_text("N")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)

    def test_custom_confirm(self):
        self.inp.send_text("s")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
            confirm_letter="s",
        )
        result = confirm_prompt._session.prompt()
        self.assertEqual(result, True)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], True)

        self.inp.send_text("S")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
            confirm_letter="s",
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, True)

    def test_custom_reject(self):
        self.inp.send_text("w")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=False,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
            reject_letter="w",
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)
        self.assertEqual(confirm_prompt.status["answered"], True)
        self.assertEqual(confirm_prompt.status["result"], False)

        self.inp.send_text("W")
        confirm_prompt = ConfirmPrompt(
            message="hello",
            style=None,
            default=True,
            qmark="?",
            output=DummyOutput(),
            input=self.inp,
            reject_letter="w",
        )
        result = confirm_prompt.execute()
        self.assertEqual(result, False)

    def test_get_prompt_message(self):
        confirm_prompt = ConfirmPrompt(
            message="hello", style=None, default=True, qmark="?", confirm_letter="W"
        )
        message = confirm_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "?"),
                ("class:question", " hello"),
                ("class:instruction", " (W/n) "),
            ],
        )

        confirm_prompt.status["answered"] = True
        confirm_prompt.status["result"] = True
        message = confirm_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "?"),
                ("class:answered_question", " hello"),
                ("class:answer", " Yes"),
            ],
        )

        confirm_prompt = ConfirmPrompt(
            message="Are you sure?",
            style=None,
            default=False,
            qmark="x",
            amark="x",
        )
        message = confirm_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "x"),
                ("class:question", " Are you sure?"),
                ("class:instruction", " (y/N) "),
            ],
        )

        confirm_prompt.status["answered"] = True
        confirm_prompt.status["result"] = False
        message = confirm_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "x"),
                ("class:answered_question", " Are you sure?"),
                ("class:answer", " No"),
            ],
        )

        # instruction
        confirm_prompt = ConfirmPrompt(
            message="Are you sure?",
            style=None,
            default=False,
            qmark="x",
            amark="x",
            instruction="(abc)",
        )
        message = confirm_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "x"),
                ("class:question", " Are you sure?"),
                ("class:instruction", " (abc) "),
            ],
        )

    @patch("InquirerPy.prompts.confirm.ConfirmPrompt._get_prompt_message")
    @patch("InquirerPy.base.simple.Style.from_dict")
    @patch("InquirerPy.base.simple.KeyBindings")
    @patch("InquirerPy.prompts.confirm.PromptSession")
    def test_callable_called(
        self, MockedSession, MockedKeyBindings, MockedStyle, mocked_message
    ):
        ConfirmPrompt(
            message="Are you sure?",
            style=None,
            default=False,
            qmark="x",
        )
        kb = MockedKeyBindings()
        style = MockedStyle()
        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            wrap_lines=True,
            bottom_toolbar=None,
            input=None,
            output=None,
        )

    @patch.object(PromptSession, "prompt")
    def test_confirm_kbi(self, mocked_session):
        mocked_session.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        prompt = ConfirmPrompt(message="")
        self.assertRaises(KeyboardInterrupt, prompt.execute)
        mocked_session.return_value = False
        prompt.execute()
