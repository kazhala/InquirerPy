import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.key_binding.key_bindings import KeyBindings

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.rawlist import InquirerPyRawlistControl, RawlistPrompt
from InquirerPy.separator import Separator


class TestRawList(unittest.TestCase):
    options = [{"name": "foo", "value": "boo"}, "hello", Separator(), "yes"]

    def test_content_control(self):
        content_control = InquirerPyRawlistControl(self.options, "yes", " ", ")")
        self.assertEqual(content_control.pointer, "  ")
        self.assertEqual(content_control.separator, ")")
        self.assertEqual(content_control.option_count, 4)
        self.assertEqual(content_control.selected_option_index, 3)
        self.assertEqual(
            content_control._get_hover_text(content_control.options[0]),
            [
                ("class:pointer", "  "),
                ("class:pointer", "1) "),
                ("class:pointer", "foo"),
            ],
        )
        self.assertEqual(
            content_control._get_normal_text(content_control.options[0]),
            [("", "  "), ("", "1) "), ("", "foo")],
        )
        self.assertEqual(
            content_control.options,
            [
                {"actual_index": 0, "display_index": 1, "name": "foo", "value": "boo"},
                {
                    "actual_index": 1,
                    "display_index": 2,
                    "name": "hello",
                    "value": "hello",
                },
                {"name": "---------------", "value": ANY},
                {"actual_index": 3, "display_index": 3, "name": "yes", "value": "yes"},
            ],
        )
        self.assertEqual(
            content_control._get_formatted_options(),
            [
                ("", "  "),
                ("", "1) "),
                ("", "foo"),
                ("", "\n"),
                ("", "  "),
                ("", "2) "),
                ("", "hello"),
                ("", "\n"),
                ("", "  "),
                ("", "---------------"),
                ("", "\n"),
                ("class:pointer", "  "),
                ("class:pointer", "3) "),
                ("class:pointer", "yes"),
            ],
        )

        content_control = InquirerPyRawlistControl(self.options, 2, " ", ")")
        self.assertEqual(content_control.selected_option_index, 1)

    def test_content_control_exceptions(self):
        options = [{"hello": "hello"}]
        self.assertRaises(
            RequiredKeyNotFound, InquirerPyRawlistControl, options, "", "", ""
        )

        options = [Separator(), Separator()]
        self.assertRaises(
            InvalidArgument, InquirerPyRawlistControl, options, "", "", ""
        )

        options = []
        self.assertRaises(
            InvalidArgument, InquirerPyRawlistControl, options, "", "", ""
        )

    def test_prompt(self):
        rawlist_prompt = RawlistPrompt(
            message="hello",
            options=self.options,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(rawlist_prompt.instruction, "bb")
        self.assertEqual(rawlist_prompt.message, "hello")

    def test_minimum_args(self):
        RawlistPrompt(message="what", options=self.options)

    def test_prompt_message(self):
        prompt = RawlistPrompt(
            message="hello",
            options=self.options,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:symbol", "?"),
                ("class:question", " hello"),
                ("class:instruction", " bb"),
            ],
        )
        prompt.status["answered"] = True
        prompt.status["result"] = []
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:symbol", "?"),
                ("class:question", " hello"),
                ("class:answer", " []"),
            ],
        )

    def test_prompt_bindings(self):
        prompt = RawlistPrompt(
            message="hello",
            options=self.options,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 0)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 1)

        self.assertEqual(prompt.status, {"result": None, "answered": False})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"result": "hello", "answered": True})

    @patch.object(KeyBindings, "add")
    def test_kb_added(self, mocked_add):
        RawlistPrompt(
            message="hello",
            options=self.options,
            default="hello",
            separator=".",
            instruction="bb",
        )
        mocked_add.assert_has_calls([call("1")])
        mocked_add.assert_has_calls([call("2")])
        mocked_add.assert_has_calls([call("3")])
