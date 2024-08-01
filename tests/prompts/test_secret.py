import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.utils import InquirerPyStyle
from InquirerPy.validator import PasswordValidator
from tests.style import get_sample_style


class TestSecret(unittest.TestCase):
    def test_prompt_result(self):
        with create_pipe_input() as inp:
            inp.send_text("what\n")
            secret_prompt = SecretPrompt(
                message="hello",
                style=InquirerPyStyle({"answer": ""}),
                default="yes",
                qmark="~",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
            )
            result = secret_prompt.execute()
            self.assertEqual(result, "yeswhat")
            self.assertEqual(
                secret_prompt.status,
                {"answered": True, "result": "yeswhat", "skipped": False},
            )

    @patch.object(Buffer, "validate_and_handle")
    def test_prompt_validation(self, mocked_validate):
        def _hello():
            secret_prompt._session.app.exit(result="yes")

        with create_pipe_input() as inp:
            mocked_validate.side_effect = _hello
            inp.send_text("afas\n")
            secret_prompt = SecretPrompt(
                message="what",
                style=InquirerPyStyle({}),
                validate=PasswordValidator(length=8),
                input=inp,
                output=DummyOutput(),
            )
            result = secret_prompt.execute()
            mocked_validate.assert_called_once()
            self.assertEqual(result, "yes")
            self.assertEqual(secret_prompt.status["answered"], False)
            self.assertEqual(secret_prompt.status["result"], None)

    def test_prompt_message(self):
        secret_prompt = SecretPrompt(
            message="fooboo", style=InquirerPyStyle({}), qmark="[?]", vi_mode=True
        )
        message = secret_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " fooboo"),
                ("class:instruction", " "),
            ],
        )

        secret_prompt.status["answered"] = True
        secret_prompt.status["result"] = "hello"
        message = secret_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "?"),
                ("class:answered_question", " fooboo"),
                ("class:answer", " *****"),
            ],
        )

        # instruction
        secret_prompt = SecretPrompt(
            message="fooboo",
            style=InquirerPyStyle({}),
            qmark="[?]",
            vi_mode=True,
            instruction="(abc)",
        )
        message = secret_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " fooboo"),
                ("class:instruction", " (abc) "),
            ],
        )

    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.secret.SecretPrompt._get_prompt_message")
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
        kb = MockedKeyBindings()
        style = MockedStyle()
        lexer = MockedLexer()
        SecretPrompt(
            message="what",
            style=None,
            default="111",
            qmark="[!]",
            vi_mode=True,
        )

        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            completer=None,
            validator=ANY,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.VI,
            lexer=lexer,
            is_password=True,
            multiline=False,
            complete_style=CompleteStyle.COLUMN,
            wrap_lines=True,
            bottom_toolbar=None,
        )
        MockedStyle.assert_has_calls(
            [
                call(),
                call(get_sample_style()),
            ]
        )
        MockedLexer.assert_has_calls([call("class:input")])

    def test_invalid_argument(self):
        self.assertRaises(InvalidArgument, SecretPrompt, "hello", None, 12)
        SecretPrompt(message="hello", default=lambda _: "12")
