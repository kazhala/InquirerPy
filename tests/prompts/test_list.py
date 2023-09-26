import unittest
from unittest.mock import patch

from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT, INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.list import InquirerPyListControl, ListPrompt
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle


class TestListPrompt(unittest.TestCase):
    choices = [
        {"name": "apple", "value": "peach"},
        "pear",
        {"name": "melon", "value": "watermelon"},
    ]

    def test_list_control_enabled(self) -> None:
        list_control = InquirerPyListControl(
            [
                {"name": "apple", "value": "peach", "enabled": True},
                "pear",
                {"name": "melon", "value": "watermelon"},
            ],
            "watermelon",
            INQUIRERPY_POINTER_SEQUENCE,
            ">",
            None,
            True,
            " ",
        )
        self.assertEqual(
            list_control.choices,
            [
                {"name": "apple", "value": "peach", "enabled": True},
                {"name": "pear", "value": "pear", "enabled": False},
                {"name": "melon", "value": "watermelon", "enabled": False},
            ],
        )

    def test_list_control_exceptions(self):
        self.assertRaises(
            RequiredKeyNotFound,
            InquirerPyListControl,
            [
                {"what": "apple", "value": "peach"},
                "pear",
            ],
            "watermelon",
            "",
            "",
            None,
            False,
            " ",
        )
        self.assertRaises(
            InvalidArgument, InquirerPyListControl, [], "", "", "", None, False, " "
        )

    def test_choice_combination(self):
        prompt = ListPrompt(message="Test combo", choices=["hello"])
        self.assertEqual(prompt._qmark, "?")
        self.assertEqual(prompt.instruction, "")

        self.assertRaises(InvalidArgument, ListPrompt, "", [Separator(), Separator()])

    def test_list_prompt_message(self):
        prompt = ListPrompt(
            message="Select a fruit",
            choices=self.choices,
            default="watermelon",
            style=InquirerPyStyle({"pointer": "#61afef"}),
            vi_mode=True,
            qmark="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "[?]"),
                ("class:question", " Select a fruit"),
                ("class:instruction", " (j/k) "),
            ],
        )

    def test_list_bindings(self):
        prompt = ListPrompt(
            message="Select a fruit",
            choices=self.choices,
            default="watermelon",
            style=InquirerPyStyle({"pointer": "#61afef"}),
            vi_mode=True,
            qmark="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 2)

        self.assertEqual(
            prompt.status, {"result": None, "answered": False, "skipped": False}
        )
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(
            prompt.status, {"result": "melon", "answered": True, "skipped": False}
        )

    def test_separator_movement(self):
        prompt = ListPrompt(message="..", choices=[Separator("hello"), "yes"])
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)

        prompt = ListPrompt(
            message="..", choices=[Separator("hello"), "yes", Separator(), "no"]
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 3)

    def test_list_enter_empty(self):
        prompt = ListPrompt(
            message="",
            choices=["haha", "haah", "what", "I don't know"],
        )
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
            self.assertEqual(prompt.status["result"], "haha")

        prompt = ListPrompt(
            message="",
            choices=["haha", "haah", "what", "I don't know"],
            multiselect=True,
        )
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
            self.assertEqual(prompt.status["result"], ["haha"])
            prompt.content_control.choices[1]["enabled"] = True
            prompt._handle_enter(event)
            self.assertEqual(prompt.status["result"], ["haah"])

    @patch("InquirerPy.base.complex.Application.run")
    def test_prompt_execute(self, mocked_run):
        mocked_run.return_value = "hello"
        result = ListPrompt("hello world", ["yes", "no"]).execute()
        self.assertEqual(result, "hello")

        result = ListPrompt(
            "hello world", ["yes", "no"], filter=lambda _: "no"
        ).execute()
        self.assertEqual(result, "no")

        mocked_run.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        prompt = ListPrompt("hello world", ["yes", "no"], filter=lambda _: "no")
        self.assertRaises(KeyboardInterrupt, prompt.execute)

        mocked_run.return_value = INQUIRERPY_KEYBOARD_INTERRUPT
        prompt = ListPrompt("hello world", ["yes", "no"])
        try:
            result = prompt.execute(raise_keyboard_interrupt=False)
        except KeyboardInterrupt:
            self.assertFalse(prompt._is_raising_kbi())
        else:
            self.fail("should raise kbi")
