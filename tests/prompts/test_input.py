import os
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
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_prompt_result(self):
        self.inp.send_text("hello\n")
        input_prompt = InputPrompt(
            message="yes",
            style=None,
            default="world",
            qmark="!",
            vi_mode=False,
            input=self.inp,
            output=DummyOutput(),
        )
        result = input_prompt.execute()
        self.assertEqual(result, "worldhello")
        self.assertEqual(
            input_prompt.status, {"answered": True, "result": "worldhello"}
        )

    def test_prompt_filter(self):
        self.inp.send_text("hello\n")
        input_prompt = InputPrompt(
            message="yes",
            style=None,
            default="world",
            qmark="!",
            vi_mode=False,
            input=self.inp,
            output=DummyOutput(),
            filter=lambda x: x * 2,
            transformer=lambda x: "what",
        )
        result = input_prompt.execute()
        self.assertEqual(result, "worldhelloworldhello")
        self.assertEqual(
            input_prompt.status, {"answered": True, "result": "worldhello"}
        )
        self.assertEqual(
            input_prompt._get_prompt_message(),
            [
                ("class:answermark", "?"),
                ("class:answered_question", " yes"),
                ("class:answer", " what"),
            ],
        )

    def test_prompt_result_multiline(self):
        self.inp.send_text("hello\nworld\nfoo\nboo\x1b\r")
        input_prompt = InputPrompt(
            message="yes",
            style=None,
            default="",
            qmark="!",
            vi_mode=False,
            input=self.inp,
            output=DummyOutput(),
            multiline=True,
        )
        result = input_prompt.execute()
        self.assertEqual(result, "hello\nworld\nfoo\nboo")
        self.assertEqual(
            input_prompt.status, {"answered": True, "result": "hello\nworld\nfoo\nboo"}
        )

    def test_prompt_completion(self):
        input_prompt = InputPrompt(
            message="yes",
            style=None,
            default="",
            qmark="!",
            vi_mode=False,
            input=self.inp,
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

    def test_prompt_message(self):
        input_prompt = InputPrompt(message="Enter your name", style=None, qmark="[?]")
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Enter your name"),
                ("class:instruction", " "),
            ],
        )
        input_prompt.status["answered"] = True
        input_prompt.status["result"] = "haha"
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:answermark", "?"),
                ("class:answered_question", " Enter your name"),
                ("class:answer", " haha"),
            ],
        )

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

    @patch("InquirerPy.prompts.input.Validator.from_callable")
    @patch("InquirerPy.prompts.input.NestedCompleter.from_nested_dict")
    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.input.InputPrompt._get_prompt_message")
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
        mocked_completer,
        mocked_validator,
    ):
        completer = mocked_completer()
        validate = mocked_validator()
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
            validator=validate,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.EMACS,
            lexer=lexer,
            is_password=False,
            multiline=True,
            complete_style=CompleteStyle.COLUMN,
        )
        mocked_validator.assert_has_calls(
            [call(ANY, "Invalid input", move_cursor_to_end=True)]
        )
        mocked_completer.assert_has_calls(
            [call({"hello": None, "hey": None, "what": None})]
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

    def test_vi_kb(self):
        prompt = InputPrompt(message="")
        self.assertEqual(prompt._editing_mode, EditingMode.EMACS)
        prompt = InputPrompt(message="", vi_mode=True)
        self.assertEqual(prompt._editing_mode, EditingMode.VI)
        os.environ["INQUIRERPY_VI_MODE"] = "true"
        prompt = InputPrompt(message="")
        self.assertEqual(prompt._editing_mode, EditingMode.VI)
        prompt = InputPrompt(message="", vi_mode=False)
        self.assertEqual(prompt._editing_mode, EditingMode.VI)

    def test_message_call(self):
        prompt = InputPrompt(message=lambda result: "Hello" if not result else "yes")
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Hello"),
                ("class:instruction", " "),
            ],
        )
