import unittest
from unittest.mock import patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.styles.style import Style

from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
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
        )
        self.assertEqual(
            list_control.choices,
            [
                {"name": "apple", "value": "peach", "enabled": True},
                {"name": "pear", "value": "pear", "enabled": False},
                {"name": "melon", "value": "watermelon", "enabled": False},
            ],
        )

    def test_list_control(self):
        list_control = InquirerPyListControl(
            self.choices, "watermelon", INQUIRERPY_POINTER_SEQUENCE, ">", None, False
        )
        self.assertEqual(
            list_control.choices,
            [
                {"name": "apple", "value": "peach", "enabled": False},
                {"name": "pear", "value": "pear", "enabled": False},
                {"name": "melon", "value": "watermelon", "enabled": False},
            ],
        )
        self.assertEqual(list_control.selected_choice_index, 2)
        self.assertEqual(
            list_control._get_formatted_choices(),
            [
                ("", " "),
                ("class:marker", " "),
                ("", "apple"),
                ("", "\n"),
                ("", " "),
                ("class:marker", " "),
                ("", "pear"),
                ("", "\n"),
                ("class:pointer", "❯"),
                ("class:marker", " "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "melon"),
            ],
        )
        self.assertEqual(list_control.choice_count, 3)
        self.assertEqual(
            list_control.selection,
            {"name": "melon", "value": "watermelon", "enabled": False},
        )
        list_control.choices[0]["enabled"] = True
        list_control.choices[1]["enabled"] = True
        self.assertEqual(
            list_control._get_formatted_choices(),
            [
                ("", " "),
                ("class:marker", ">"),
                ("", "apple"),
                ("", "\n"),
                ("", " "),
                ("class:marker", ">"),
                ("", "pear"),
                ("", "\n"),
                ("class:pointer", "❯"),
                ("class:marker", " "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "melon"),
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
        )
        self.assertRaises(
            InvalidArgument, InquirerPyListControl, [], "", "", "", None, False
        )

    def test_list_prompt(self):
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
        self.assertEqual(prompt._editing_mode, EditingMode.VI)
        self.assertIsInstance(prompt.content_control, InquirerPyListControl)
        self.assertIsInstance(prompt._kb, KeyBindings)
        self.assertIsInstance(prompt._style, Style)
        self.assertEqual(prompt._message, "Select a fruit")
        self.assertEqual(prompt._qmark, "[?]")
        self.assertEqual(prompt.instruction, "(j/k)")

        window_list = list(prompt.layout.children)
        self.assertEqual(len(window_list), 4)
        self.assertIsInstance(window_list[0], Window)
        self.assertIsInstance(window_list[1], ConditionalContainer)
        self.assertIsInstance(window_list[2], ConditionalContainer)

    def test_minimum_args(self):
        ListPrompt(
            message="Select a fruit",
            choices=self.choices,
            style=InquirerPyStyle({}),
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

    def test_after_render(self):
        prompt = ListPrompt(message="", choices=lambda _: [1, 2, 3])
        self.assertEqual(prompt.content_control.choices, [])
        prompt._after_render("")
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "1", "value": 1},
                {"enabled": False, "name": "2", "value": 2},
                {"enabled": False, "name": "3", "value": 3},
            ],
        )

    def test_prompt_filter(self):
        prompt = ListPrompt(
            message="",
            choices=[1, 2, 3],
            filter=lambda x: x * 2,
            transformer=lambda x: x * 3,
        )
        prompt.status = {"answered": True, "result": 1}
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:answermark", "?"),
                ("class:answered_question", " "),
                ("class:answer", " 3"),
            ],
        )
        self.assertEqual(prompt._filter(1), 2)

    def test_prompt_message_with_cursor(self):
        prompt = ListPrompt(message="Select one:", choices=[1, 2, 3])
        self.assertEqual(
            prompt._get_prompt_message_with_cursor(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one:"),
                ("class:instruction", " "),
                ("[SetCursorPosition]", ""),
                ("", " "),
            ],
        )

    def test_prompt_cycle(self):
        choices = [
            {"name": "apple", "value": "peach"},
            "pear",
            {"name": "melon", "value": "watermelon"},
        ]
        prompt = ListPrompt(message="hello", choices=choices, cycle=False)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 2)

        choices = [
            Separator(),
            {"name": "apple", "value": "peach"},
            "pear",
            {"name": "melon", "value": "watermelon"},
            Separator(),
        ]
        prompt = ListPrompt(message="hello", choices=choices, cycle=False)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
