import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from InquirerPy.prompts.secret import SecretPrompt
from InquirerPy.utils import InquirerPyStyle
from InquirerPy.validator import PasswordValidator


class TestSecret(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_prompt_result(self):
        self.inp.send_text("what\n")
        secret_prompt = SecretPrompt(
            message="hello",
            style=InquirerPyStyle({"answer": ""}),
            default="yes",
            qmark="~",
            vi_mode=False,
            input=self.inp,
            output=DummyOutput(),
        )
        result = secret_prompt.execute()
        self.assertEqual(result, "yeswhat")
        self.assertEqual(secret_prompt.status, {"answered": True, "result": "yeswhat"})

    @patch.object(Buffer, "validate_and_handle")
    def test_prompt_validation(self, mocked_validate):
        def _hello():
            secret_prompt._session.app.exit(result="yes")

        mocked_validate.side_effect = _hello
        self.inp.send_text("afas\n")
        secret_prompt = SecretPrompt(
            message="what",
            style=InquirerPyStyle({}),
            validate=PasswordValidator(length=8),
            input=self.inp,
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

    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.secret.SecretPrompt._get_prompt_message")
    @patch("InquirerPy.base.Style.from_dict")
    @patch("InquirerPy.base.KeyBindings")
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
        )
        MockedStyle.assert_has_calls(
            [
                call(),
                call(
                    {
                        "questionmark": "#e5c07b",
                        "answermark": "#e5c07b",
                        "answer": "#61afef",
                        "input": "#98c379",
                        "question": "",
                        "answered_question": "",
                        "instruction": "",
                        "pointer": "#61afef",
                        "checkbox": "#98c379",
                        "separator": "",
                        "skipped": "#5c6370",
                        "validator": "",
                        "marker": "#e5c07b",
                        "fuzzy_prompt": "#c678dd",
                        "fuzzy_info": "#56b6c2",
                        "fuzzy_match": "#c678dd",
                        "frame.border": "#4b5263",
                    }
                ),
            ]
        )
        MockedLexer.assert_has_calls([call("class:input")])
