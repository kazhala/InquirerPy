import asyncio
import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.prompts.input import InputPrompt


class TestInputPrompt(unittest.TestCase):
    def test_prompt_result(self):
        with create_pipe_input() as inp:
            inp.send_text("hello\n")
            input_prompt = InputPrompt(
                message="yes",
                style=None,
                default="world",
                qmark="!",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
            )
            result = input_prompt.execute()
            self.assertEqual(result, "worldhello")
            self.assertEqual(input_prompt.status["answered"], True)
            self.assertEqual(input_prompt.status["result"], "worldhello")
            self.assertEqual(input_prompt.status["skipped"], False)

    def test_prompt_filter(self):
        with create_pipe_input() as inp:
            inp.send_text("hello\n")
            input_prompt = InputPrompt(
                message="yes",
                style=None,
                default="world",
                qmark="!",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
                filter=lambda x: x * 2,
                transformer=lambda _: "what",
            )
            result = input_prompt.execute()
            self.assertEqual(result, "worldhelloworldhello")
            self.assertEqual(input_prompt.status["answered"], True)
            self.assertEqual(input_prompt.status["result"], "worldhello")
            self.assertEqual(
                input_prompt._get_prompt_message(),
                [
                    ("class:answermark", "?"),
                    ("class:answered_question", " yes"),
                    ("class:answer", " what"),
                ],
            )

    def test_prompt_result_multiline(self):
        with create_pipe_input() as inp:
            inp.send_text("hello\nworld\nfoo\nboo\x1b\r")
            input_prompt = InputPrompt(
                message="yes",
                style=None,
                default="",
                qmark="!",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
                multiline=True,
            )
            result = input_prompt.execute()
            self.assertEqual(result, "hello\nworld\nfoo\nboo")
            self.assertEqual(input_prompt.status["answered"], True)
            self.assertEqual(input_prompt.status["result"], "hello\nworld\nfoo\nboo")
            self.assertEqual(input_prompt.status["skipped"], False)

    def test_prompt_completion(self):
        with create_pipe_input() as inp:
            input_prompt = InputPrompt(
                message="yes",
                style=None,
                default="",
                qmark="!",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
                multiline=True,
                completer={"hello": None, "hey": None, "what": None},
            )

            completer = input_prompt._completer
            doc_text = "he"
            doc = Document(doc_text, len(doc_text))
            event = CompleteEvent()
            completions = [
                completion.text
                for completion in list(completer.get_completions(doc, event))  # type: ignore
            ]
            self.assertEqual(sorted(completions), ["hello", "hey"])

    def test_prompt_message_multiline(self):
        input_prompt = InputPrompt(
            message="Enter your name",
            style=None,
            default="",
            qmark="[?]",
            vi_mode=False,
            multiline=True,
            completer={"hello": None, "hey": None, "what": None},
        )
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Enter your name"),
                ("class:instruction", " ESC + Enter to finish input"),
                ("class:questionmark", "\n%s " % INQUIRERPY_POINTER_SEQUENCE),
            ],
        )
        input_prompt.status["answered"] = True
        input_prompt.status["result"] = "haha\n123"
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "?"),
                ("class:answered_question", " Enter your name"),
                ("class:answer", " haha...[3 chars]"),
            ],
        )

    def test_prompt_message_instruction(self):
        input_prompt = InputPrompt(
            message="Enter your name:",
            style=None,
            default="",
            qmark="[?]",
            vi_mode=False,
            instruction="(abc)",
        )
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Enter your name:"),
                ("class:instruction", " (abc) "),
            ],
        )

        input_prompt = InputPrompt(
            message="Enter your name:",
            style=None,
            default="",
            qmark="[?]",
            vi_mode=False,
            instruction="(abc)",
            multiline=True,
        )
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Enter your name:"),
                ("class:instruction", " (abc) "),
                ("class:questionmark", "\n%s " % INQUIRERPY_POINTER_SEQUENCE),
            ],
        )

    @patch("InquirerPy.prompts.input.NestedCompleter.from_nested_dict")
    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.input.InputPrompt._get_prompt_message")
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
        mocked_completer,
    ):
        completer = mocked_completer()
        kb = MockedKeyBindings()
        style = MockedStyle()
        lexer = MockedLexer()
        InputPrompt(
            message="Enter your name",
            style=None,
            default="",
            qmark="[?]",
            vi_mode=False,
            multiline=True,
            completer={"hello": None, "hey": None, "what": None},
        )
        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            completer=completer,
            validator=ANY,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.EMACS,
            lexer=lexer,
            is_password=False,
            multiline=True,
            complete_style=CompleteStyle.COLUMN,
            wrap_lines=True,
            bottom_toolbar=None,
        )
        mocked_completer.assert_has_calls(
            [call({"hello": None, "hey": None, "what": None})]
        )
        MockedLexer.assert_has_calls([call("class:input")])

    @patch("InquirerPy.prompts.input.PromptSession")
    def test_long_instruction(self, MockedSession):
        InputPrompt(message="", long_instruction="asfasdf")

        MockedSession.assert_called_once_with(
            message=ANY,
            key_bindings=ANY,
            style=ANY,
            completer=ANY,
            validator=ANY,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.EMACS,
            lexer=ANY,
            is_password=False,
            multiline=False,
            complete_style=CompleteStyle.COLUMN,
            wrap_lines=True,
            bottom_toolbar=[("class:long_instruction", "asfasdf")],
        )

    def test_handle_completion(self):
        prompt = InputPrompt(message="")
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_completion(event)
            mock.assert_not_called()

        prompt = InputPrompt(message="", completer={})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_completion(event)
            mock.assert_has_calls(
                [
                    call().app.current_buffer.complete_state.__bool__(),
                    call().app.current_buffer.complete_next(),
                ]
            )

    def test_prompt_result_async(self):
        with create_pipe_input() as inp:
            inp.send_text("hello\n")
            input_prompt = InputPrompt(
                message="yes",
                style=None,
                default="world",
                qmark="!",
                vi_mode=False,
                input=inp,
                output=DummyOutput(),
            )
            result = asyncio.run(input_prompt.execute_async())
            self.assertEqual(result, "worldhello")
            self.assertEqual(input_prompt.status["answered"], True)
            self.assertEqual(input_prompt.status["result"], "worldhello")
            self.assertEqual(input_prompt.status["skipped"], False)
