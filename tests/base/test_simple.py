import os
import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import Condition

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
from InquirerPy.prompts.input import InputPrompt
from InquirerPy.utils import get_style
from InquirerPy.validator import NumberValidator
from tests.style import get_sample_style


class TestBaseSimple(unittest.TestCase):
    @patch("InquirerPy.base.simple.KeyBindings.add")
    @patch("InquirerPy.base.simple.Validator.from_callable")
    @patch("InquirerPy.base.simple.Style.from_dict")
    def test_constructor_default(self, mocked_style, mocked_validator, mocked_kb):
        input_prompt = InputPrompt(message="Enter your name", style=None, default="1")
        self.assertEqual(input_prompt._message, "Enter your name")
        mocked_style.assert_has_calls([call(get_sample_style())])
        self.assertEqual(input_prompt._default, "1")
        self.assertEqual(input_prompt._qmark, "?")
        self.assertEqual(input_prompt._amark, "?")
        self.assertEqual(input_prompt._editing_mode, EditingMode.EMACS)
        mocked_validator.assert_has_calls(
            [call(ANY, "Invalid input", move_cursor_to_end=True)]
        )
        mocked_kb.assert_has_calls([call("c-c")])

    @patch("InquirerPy.base.simple.Validator.from_callable")
    @patch("InquirerPy.base.simple.Style.from_dict")
    def test_constructor_custom(self, mocked_style, mocked_validator):
        input_prompt = InputPrompt(
            message=lambda _: "Enter your name",
            style=get_style({"questionmark": "#111111"}, style_override=False),
            qmark="[?]",
            amark="*",
            default=lambda _: "1",
            vi_mode=True,
            validate=NumberValidator(),
        )
        style = get_sample_style()
        style["questionmark"] = "#111111"
        self.assertEqual(input_prompt._message, "Enter your name")
        mocked_style.assert_has_calls([call(style)])
        self.assertEqual(input_prompt._default, "1")
        self.assertEqual(input_prompt._qmark, "[?]")
        self.assertEqual(input_prompt._amark, "*")
        self.assertEqual(input_prompt._editing_mode, EditingMode.VI)
        mocked_validator.assert_not_called()

    def test_vi_kb(self):
        prompt = InputPrompt(message="")
        self.assertEqual(prompt._editing_mode, EditingMode.EMACS)
        os.environ["INQUIRERPY_VI_MODE"] = "true"
        prompt = InputPrompt(message="")
        self.assertEqual(prompt._editing_mode, EditingMode.VI)
        prompt = InputPrompt(message="", vi_mode=False)
        self.assertEqual(prompt._editing_mode, EditingMode.VI)
        del os.environ["INQUIRERPY_VI_MODE"]

    def test_prompt_message_initial(self):
        input_prompt = InputPrompt(message="Enter your name", style=None, qmark="[?]")
        message = input_prompt._get_prompt_message()
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Enter your name"),
                ("class:instruction", " "),
            ],
        )

    def test_prompt_message_answered(self):
        input_prompt = InputPrompt(message="Enter your name", style=None, qmark="[?]")
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

    def test_prompt_message_kbi(self):
        input_prompt = InputPrompt(message="Enter your name", style=None, qmark="[?]")
        input_prompt.status["answered"] = True
        input_prompt.status["result"] = INQUIRERPY_KEYBOARD_INTERRUPT
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message, [("class:skipped", "[?]"), ("class:skipped", " Enter your name ")]
        )

    @patch("InquirerPy.base.simple.KeyBindings.add")
    def test_register_kb(self, mocked_kb):
        prompt = InputPrompt(message="")
        hello = prompt.register_kb("alt-a", "alt-b", filter=True)

        @hello
        def _(_):  # type:ignore
            pass

        mocked_kb.assert_has_calls([call("escape", "a", "escape", "b", filter=True)])

        condition = Condition(lambda: True)
        hello = prompt.register_kb("c-i", filter=condition)

        @hello
        def _(_):
            pass

        mocked_kb.assert_has_calls([call("c-i", filter=condition)])

    @patch.object(InputPrompt, "_run")
    def test_execute_kbi(self, mocked_run):
        prompt = InputPrompt(message="")
        mocked_run.return_value = INQUIRERPY_KEYBOARD_INTERRUPT

        result = prompt.execute(raise_keyboard_interrupt=False)
        self.assertEqual(result, None)

        self.assertRaises(KeyboardInterrupt, prompt.execute, True)

        os.environ["INQUIRERPY_NO_RAISE_KBI"] = "True"
        result = InputPrompt(message="").execute()
        result = InputPrompt(message="", raise_keyboard_interrupt=True).execute()
        result = InputPrompt(message="").execute(raise_keyboard_interrupt=True)
        del os.environ["INQUIRERPY_NO_RAISE_KBI"]

    @patch.object(InputPrompt, "_run")
    def test_execute_filter(self, mocked_run):
        mocked_run.return_value = "1"
        prompt = InputPrompt(message="")
        result = prompt.execute()
        self.assertEqual(result, "1")

        prompt = InputPrompt(message="", filter=lambda result: int(result) * 2)
        result = prompt.execute()
        self.assertEqual(result, 2)
