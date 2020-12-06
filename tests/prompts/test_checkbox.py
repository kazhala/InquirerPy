import unittest
from unittest.mock import ANY, patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.styles.style import Style

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.checkbox import CheckboxPrompt, InquirerPyCheckboxControl
from InquirerPy.separator import Separator


class TestCheckbox(unittest.TestCase):
    separator = Separator()
    options = [
        "boy",
        "girl",
        separator,
        {"name": "mix", "value": "boy&girl", "enabled": True},
    ]

    def test_checkbox_control(self):
        checkbox_control = InquirerPyCheckboxControl(self.options, "boy&girl")
        self.assertEqual(
            checkbox_control.options,
            [
                {"name": "boy", "value": "boy", "enabled": False},
                {"name": "girl", "value": "girl", "enabled": False},
                {"name": 15 * "-", "value": self.separator, "enabled": False},
                {"name": "mix", "value": "boy&girl", "enabled": True},
            ],
        )
        self.assertEqual(checkbox_control.selected_option_index, 3)
        self.assertEqual(
            checkbox_control._get_formatted_options(),
            [
                ("", "   "),
                ("class:checkbox", "⬡ "),
                ("", "boy"),
                ("", "\n"),
                ("", "   "),
                ("class:checkbox", "⬡ "),
                ("", "girl"),
                ("", "\n"),
                ("", "   "),
                ("", "---------------"),
                ("", "\n"),
                ("class:pointer", " ❯ "),
                ("class:checkbox", "⬢ "),
                ("class:pointer", "mix"),
            ],
        )
        self.assertEqual(checkbox_control.option_count, 4)
        self.assertEqual(
            checkbox_control.selection,
            {"name": "mix", "value": "boy&girl", "enabled": True},
        )

    def test_checkbox_control_exceptions(self):
        self.assertRaises(
            RequiredKeyNotFound,
            InquirerPyCheckboxControl,
            [
                {"what": "apple", "value": "peach"},
                "pear",
            ],
            "watermelon",
        )
        self.assertRaises(InvalidArgument, InquirerPyCheckboxControl, [])
        self.assertRaises(
            InvalidArgument, InquirerPyCheckboxControl, "", [Separator(), Separator()]
        )

    def test_checkbox_prompt(self):
        prompt = CheckboxPrompt(
            message="Select something",
            options=self.options,
            default="boy&girl",
            style={},
            editing_mode="emacs",
            symbol="!",
            pointer="<",
            instruction="TAB",
        )
        self.assertEqual(prompt.editing_mode, EditingMode.EMACS)
        self.assertIsInstance(prompt.content_control, InquirerPyCheckboxControl)
        self.assertIsInstance(prompt.kb, KeyBindings)
        self.assertIsInstance(prompt.question_style, Style)
        self.assertEqual(prompt.message, "Select something")
        self.assertEqual(prompt.symbol, "!")
        self.assertEqual(prompt.instruction, "TAB")

    def test_minimum_args(self):
        CheckboxPrompt(message="yes", options=self.options)

    def test_checkbox_prompt_message(self):
        prompt = CheckboxPrompt(
            message="Select something",
            options=self.options,
            instruction="TAB",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:symbol", "?"),
                ("class:question", " Select something"),
                ("class:instruction", " TAB"),
            ],
        )

    def test_checkbox_bindings(self):
        prompt = CheckboxPrompt(message="", options=self.options)
        self.assertEqual(prompt.content_control.selected_option_index, 0)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 1)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
        prompt.handle_down()
        self.assertEqual(prompt.content_control.selected_option_index, 0)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 3)
        prompt.handle_up()
        self.assertEqual(prompt.content_control.selected_option_index, 1)

        self.assertEqual(prompt.status, {"result": None, "answered": False})
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt.handle_enter(event)
        self.assertEqual(prompt.status, {"result": ["mix"], "answered": True})

        prompt._toggle_option()
        self.assertEqual(
            prompt.content_control.options,
            [
                {"enabled": False, "name": "boy", "value": "boy"},
                {"enabled": True, "name": "girl", "value": "girl"},
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": True, "name": "mix", "value": "boy&girl"},
            ],
        )
