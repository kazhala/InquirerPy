import unittest
from unittest.mock import patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.styles.style import Style

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.list import InquirerPyListControl, ListPrompt
from InquirerPy.separator import Separator


class TestListPrompt(unittest.TestCase):
    choices = [
        {"name": "apple", "value": "peach"},
        "pear",
        {"name": "melon", "value": "watermelon"},
    ]

    def test_list_control(self):
        list_control = InquirerPyListControl(
            self.choices,
            "watermelon",
        )
        self.assertEqual(
            list_control.choices,
            [
                {"name": "apple", "value": "peach"},
                {"name": "pear", "value": "pear"},
                {"name": "melon", "value": "watermelon"},
            ],
        )
        self.assertEqual(list_control.selected_choice_index, 2)
        self.assertEqual(
            list_control._get_formatted_choices(),
            [
                ("", "  "),
                ("", "apple"),
                ("", "\n"),
                ("", "  "),
                ("", "pear"),
                ("", "\n"),
                ("class:pointer", "❯ "),
                ("class:pointer", "melon"),
            ],
        )
        self.assertEqual(list_control.choice_count, 3)
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
            choices=self.choices,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            qmark="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(prompt.editing_mode, EditingMode.VI)
        self.assertIsInstance(prompt.content_control, InquirerPyListControl)
        self.assertIsInstance(prompt.kb, KeyBindings)
        self.assertIsInstance(prompt.question_style, Style)
        self.assertEqual(prompt.message, "Select a fruit")
        self.assertEqual(prompt.qmark, "[?]")
        self.assertEqual(prompt.instruction, "(j/k)")

        window_list = list(prompt.layout.children)
        self.assertEqual(len(window_list), 2)
        self.assertIsInstance(window_list[0], Window)
        self.assertIsInstance(window_list[1], ConditionalContainer)

    def test_minimum_args(self):
        ListPrompt(message="Select a fruit", choices=self.choices, style={})

    def test_choice_combination(self):
        prompt = ListPrompt(message="Test combo", choices=["hello"])
        self.assertEqual(prompt.qmark, "?")
        self.assertEqual(prompt.instruction, "")

        self.assertRaises(InvalidArgument, ListPrompt, "", [Separator(), Separator()])

    def test_list_prompt_message(self):
        prompt = ListPrompt(
            message="Select a fruit",
            choices=self.choices,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            qmark="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:qmark", "[?]"),
                ("class:question", " Select a fruit"),
                ("class:instruction", " (j/k)"),
            ],
        )

    def test_list_bindings(self):
        prompt = ListPrompt(
            message="Select a fruit",
            choices=self.choices,
            default="watermelon",
            style={"pointer": "#61afef"},
            editing_mode="vim",
            qmark="[?]",
            pointer=">",
            instruction="(j/k)",
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 2)

        self.assertEqual(prompt.status, {"result": None, "answered": False})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"result": "melon", "answered": True})

    def test_separator_movement(self):
        prompt = ListPrompt(message="..", choices=[Separator("hello"), "yes"])
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)

        prompt = ListPrompt(
            message="..", choices=[Separator("hello"), "yes", Separator(), "no"]
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
