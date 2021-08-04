import unittest
from unittest.mock import ANY, call, patch

from InquirerPy.base import BaseComplexPrompt
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.rawlist import InquirerPyRawlistControl, RawlistPrompt
from InquirerPy.separator import Separator


class TestRawList(unittest.TestCase):
    choices = [
        {"name": "foo", "value": "boo", "enabled": True},
        "hello",
        Separator(),
        "yes",
    ]

    def test_content_control(self):
        content_control = InquirerPyRawlistControl(
            self.choices, "yes", " ", ") ", ">", None, True
        )
        self.assertEqual(content_control._pointer, " ")
        self.assertEqual(content_control._separator, ") ")
        self.assertEqual(content_control.choice_count, 4)
        self.assertEqual(content_control.selected_choice_index, 3)
        self.assertEqual(
            content_control._get_hover_text(content_control.choices[0]),
            [
                ("class:pointer", " "),
                ("class:marker", ">"),
                ("class:pointer", "1) "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "foo"),
            ],
        )
        self.assertEqual(
            content_control._get_normal_text(content_control.choices[0]),
            [("", " "), ("class:marker", ">"), ("", "1) "), ("", "foo")],
        )
        self.assertEqual(
            content_control.choices,
            [
                {
                    "actual_index": 0,
                    "display_index": 1,
                    "name": "foo",
                    "value": "boo",
                    "enabled": True,
                },
                {
                    "actual_index": 1,
                    "display_index": 2,
                    "name": "hello",
                    "value": "hello",
                    "enabled": False,
                },
                {"name": "---------------", "value": ANY, "enabled": False},
                {
                    "actual_index": 3,
                    "display_index": 3,
                    "name": "yes",
                    "value": "yes",
                    "enabled": False,
                },
            ],
        )
        self.assertEqual(
            content_control._get_formatted_choices(),
            [
                ("", " "),
                ("class:marker", ">"),
                ("", "1) "),
                ("", "foo"),
                ("", "\n"),
                ("", " "),
                ("class:marker", " "),
                ("", "2) "),
                ("", "hello"),
                ("", "\n"),
                ("", " "),
                ("class:marker", " "),
                ("class:separator", "---------------"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("class:pointer", "3) "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "yes"),
            ],
        )

        content_control = InquirerPyRawlistControl(
            self.choices, 2, " ", ")", ">", None, False
        )
        self.assertEqual(content_control.selected_choice_index, 1)

    def test_content_control_exceptions(self):
        choices = [{"hello": "hello"}]
        self.assertRaises(
            RequiredKeyNotFound,
            InquirerPyRawlistControl,
            choices,
            "",
            "",
            "",
            "",
            None,
            False,
        )

        choices = [Separator(), Separator()]
        self.assertRaises(
            InvalidArgument,
            InquirerPyRawlistControl,
            choices,
            "",
            "",
            "",
            "",
            None,
            True,
        )

        choices = []
        self.assertRaises(
            InvalidArgument,
            InquirerPyRawlistControl,
            choices,
            "",
            "",
            "",
            "",
            None,
            False,
        )

    def test_prompt(self):
        rawlist_prompt = RawlistPrompt(
            message="hello",
            choices=self.choices,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(rawlist_prompt.instruction, "bb")
        self.assertEqual(rawlist_prompt._message, "hello")

    def test_minimum_args(self):
        RawlistPrompt(message="what", choices=self.choices)

    def test_prompt_message(self):
        prompt = RawlistPrompt(
            message="hello",
            choices=self.choices,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " hello"),
                ("class:instruction", " bb "),
                ("class:input", "2"),
            ],
        )
        prompt.status["answered"] = True
        prompt.status["result"] = []
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:answermark", "?"),
                ("class:answered_question", " hello"),
                ("class:answer", " []"),
            ],
        )

    def test_prompt_bindings(self):
        prompt = RawlistPrompt(
            message="hello",
            choices=self.choices,
            default="hello",
            separator=".",
            instruction="bb",
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)

        self.assertEqual(prompt.status, {"result": None, "answered": False})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"result": "hello", "answered": True})

    @patch.object(BaseComplexPrompt, "_register_kb")
    def test_kb_added(self, mocked_add):
        prompt = RawlistPrompt(
            message="hello",
            choices=self.choices,
            default="hello",
            separator=".",
            instruction="bb",
        )
        mocked_add.assert_has_calls([call("c-n", filter=ANY)])
        mocked_add.assert_has_calls([call("c-p", filter=ANY)])
        try:
            mocked_add.assert_has_calls([call("1", filter=True)])
            self.fail("choices kb should be after_render")
        except:
            pass
        prompt._after_render("")
        mocked_add.assert_has_calls([call("1")])
        mocked_add.assert_has_calls([call("2")])
        mocked_add.assert_has_calls([call("3")])

    def test_rawlist_10(self):
        prompt = RawlistPrompt(message="", choices=[i for i in range(10)])
        self.assertRaises(InvalidArgument, prompt._after_render, "")
        prompt = RawlistPrompt(message="", choices=[i for i in range(9)])
        prompt._after_render("")
