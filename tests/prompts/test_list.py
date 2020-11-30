import unittest
from unittest.mock import patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.styles.style import Style

from InquirerPy.base import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.list import InquirerPyListControl, ListPrompt
from InquirerPy.separator import Separator


class TestListPrompt(unittest.TestCase):
    options = [
        {"name": "apple", "value": "peach"},
        "pear",
        {"name": "melon", "value": "watermelon"},
    ]

    def test_list_control(self):
        list_control = InquirerPyListControl(
            self.options,
            "watermelon",
        )
        self.assertEqual(
            list_control.options,
            [
                {"name": "apple", "value": "peach"},
                {"name": "pear", "value": "pear"},
                {"name": "melon", "value": "watermelon"},
            ],
        )
        self.assertEqual(list_control.selected_option_index, 2)
        self.assertEqual(
            list_control._get_formatted_options(),
            [
                ("", "   "),
                ("", "apple"),
                ("", "\n"),
                ("", "   "),
                ("", "pear"),
                ("", "\n"),
                ("class:pointer", " ❯ "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "melon"),
            ],
        )
        self.assertEqual(list_control.option_count, 3)
        self.assertEqual(
            list_control.selection, {"name": "melon", "value": "watermelon"}
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
        )
        self.assertRaises(InvalidArgument, InquirerPyListControl, [])

    def test_list_prompt(self):
        prompt = ListPrompt(
            message="Select a fruit",
            options=self.options,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            symbol="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(prompt.editing_mode, EditingMode.VI)
        self.assertIsInstance(prompt.content_control, InquirerPyListControl)
        self.assertIsInstance(prompt.kb, KeyBindings)
        self.assertIsInstance(prompt.question_style, Style)
        self.assertEqual(prompt.message, "Select a fruit")
        self.assertEqual(prompt.symbol, "[?]")
        self.assertEqual(prompt.pointer, ">")
        self.assertEqual(prompt.instruction, "(j/k)")

        window_list = list(prompt.layout.children)
        self.assertEqual(len(window_list), 2)
        self.assertIsInstance(window_list[0], Window)
        self.assertIsInstance(window_list[1], ConditionalContainer)

    def test_minimum_args(self):
        ListPrompt(message="Select a fruit", options=self.options, style={})

    def test_option_combination(self):
        prompt = ListPrompt(message="Test combo", options=["hello"])
        self.assertEqual(prompt.symbol, "?")
        self.assertEqual(prompt.pointer, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(prompt.instruction, "")

        self.assertRaises(InvalidArgument, ListPrompt, "", [Separator(), Separator()])

    def test_list_prompt_message(self):
        prompt = ListPrompt(
            message="Select a fruit",
            options=self.options,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            symbol="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:symbol", "[?]"),
                ("class:question", " Select a fruit"),
                ("class:instruction", " (j/k)"),
            ],
        )

    def test_list_bindings(self):
        prompt = ListPrompt(
            message="Select a fruit",
            options=self.options,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            symbol="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(prompt.content_control.selected_option_index, 2)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 0)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 2)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 2)

        self.assertEqual(prompt.status, {"result": None, "answered": False})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt.handle_enter(event)
        self.assertEqual(prompt.status, {"result": "melon", "answered": True})

    def test_separator_movement(self):
        prompt = ListPrompt(message="..", options=[Separator("hello"), "yes"])
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 1)

        prompt = ListPrompt(
            message="..", options=[Separator("hello"), "yes", Separator(), "no"]
        )
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
