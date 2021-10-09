import asyncio
import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.styles.style import Style

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.checkbox import CheckboxPrompt, InquirerPyCheckboxControl
from InquirerPy.separator import Separator


class TestCheckbox(unittest.TestCase):
    separator = Separator()
    choices = [
        "boy",
        "girl",
        separator,
        {"name": "mix", "value": "boy&girl", "enabled": True},
    ]

    def test_checkbox_control(self):
        checkbox_control = InquirerPyCheckboxControl(
            self.choices, "boy&girl", "1", "2", "3", None
        )
        self.assertEqual(
            checkbox_control.choices,
            [
                {"name": "boy", "value": "boy", "enabled": False},
                {"name": "girl", "value": "girl", "enabled": False},
                {"name": 15 * "-", "value": self.separator, "enabled": False},
                {"name": "mix", "value": "boy&girl", "enabled": True},
            ],
        )
        self.assertEqual(checkbox_control.selected_choice_index, 3)
        self.assertEqual(
            checkbox_control._get_formatted_choices(),
            [
                ("", " "),
                ("", " "),
                ("class:checkbox", "3"),
                ("", " "),
                ("", "boy"),
                ("", "\n"),
                ("", " "),
                ("", " "),
                ("class:checkbox", "3"),
                ("", " "),
                ("", "girl"),
                ("", "\n"),
                ("", " "),
                ("", " "),
                ("class:separator", "---------------"),
                ("", "\n"),
                ("class:pointer", "1"),
                ("", " "),
                ("class:checkbox", "2"),
                ("", " "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "mix"),
            ],
        )
        self.assertEqual(checkbox_control.choice_count, 4)
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
            "",
            "",
            "",
            None,
        )
        self.assertRaises(
            InvalidArgument, InquirerPyCheckboxControl, [], None, "", "", "", None
        )
        self.assertRaises(
            InvalidArgument,
            InquirerPyCheckboxControl,
            [Separator(), Separator()],
            None,
            "",
            "",
            "",
            None,
        )

    def test_checkbox_prompt(self):
        prompt = CheckboxPrompt(
            message="Select something",
            choices=self.choices,
            default="boy&girl",
            style=None,
            vi_mode=False,
            qmark="!",
            pointer="<",
            instruction="TAB",
        )
        self.assertEqual(prompt._editing_mode, EditingMode.EMACS)
        self.assertIsInstance(prompt.content_control, InquirerPyCheckboxControl)
        self.assertIsInstance(prompt._kb, KeyBindings)
        self.assertIsInstance(prompt._style, Style)
        self.assertEqual(prompt._message, "Select something")
        self.assertEqual(prompt._qmark, "!")
        self.assertEqual(prompt.instruction, "TAB")

    def test_minimum_args(self):
        CheckboxPrompt(message="yes", choices=self.choices)

    def test_checkbox_prompt_message(self):
        prompt = CheckboxPrompt(
            message="Select something",
            choices=self.choices,
            instruction="TAB",
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select something"),
                ("class:instruction", " TAB "),
            ],
        )

    def test_checkbox_bindings(self):
        prompt = CheckboxPrompt(message="", choices=self.choices)
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
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
        self.assertEqual(prompt.status, {"result": ["mix"], "answered": True})

        prompt._toggle_choice()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "boy", "value": "boy"},
                {"enabled": True, "name": "girl", "value": "girl"},
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": True, "name": "mix", "value": "boy&girl"},
            ],
        )

        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": True, "name": "boy", "value": "boy"},
                {"enabled": False, "name": "girl", "value": "girl"},
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": False, "name": "mix", "value": "boy&girl"},
            ],
        )

        prompt._toggle_all(True)
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": True, "name": "boy", "value": "boy"},
                {"enabled": True, "name": "girl", "value": "girl"},
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": True, "name": "mix", "value": "boy&girl"},
            ],
        )

    def test_validator(self):
        prompt = CheckboxPrompt(
            message="",
            choices=self.choices,
            validate=lambda x: len(x) > 2,
            invalid_message="hello",
        )
        with patch("prompt_toolkit.utils.Event") as mock:
            self.assertEqual(prompt._invalid, False)
            event = mock.return_value
            prompt._handle_enter(event)
            self.assertEqual(prompt._invalid, True)
            self.assertEqual(prompt._invalid_message, "hello")

    def test_kb(self):
        prompt = CheckboxPrompt(message="", choices=self.choices)
        prompt._invalid = True

        @prompt.register_kb("b")
        def test(_):
            pass

        test("")  # type: ignore
        self.assertEqual(prompt._invalid, False)

    def test_checkbox_enter_empty(self):
        prompt = CheckboxPrompt(message="", choices=["haah", "haha", "what"])
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status["result"], [])

    def test_retrieve_choices(self) -> None:
        async def retrieve_choices(content_control) -> None:
            await content_control.retrieve_choices()

        prompt = CheckboxPrompt(message="", choices=lambda _: [1, 2, 3])
        self.assertEqual(prompt.content_control.choices, [])
        asyncio.run(retrieve_choices(prompt.content_control))
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "1", "value": 1},
                {"enabled": False, "name": "2", "value": 2},
                {"enabled": False, "name": "3", "value": 3},
            ],
        )
