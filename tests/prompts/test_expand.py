import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.key_binding.key_bindings import KeyBindings

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.expand import ExpandHelp, ExpandPrompt, InquirerPyExpandControl
from InquirerPy.separator import Separator


class TestExpandPrompt(unittest.TestCase):
    choices = [
        Separator(),
        {"name": "hello", "value": "world", "key": "b"},
        Separator("**********"),
        {"name": "foo", "value": "boo", "key": "f"},
    ]

    def test_content_control(self):
        content_control = InquirerPyExpandControl(
            choices=self.choices,
            default="f",
            help_msg="(haha)",
            expand_pointer=">>",
            pointer=" ",
            separator=")",
            marker=">",
        )
        self.assertEqual(content_control._pointer, " ")
        self.assertEqual(content_control._marker, ">")
        self.assertEqual(content_control._separator, ")")
        self.assertEqual(content_control._expanded, False)
        self.assertEqual(content_control._key_maps, {"b": 1, "f": 3, "h": 4})
        self.assertEqual(content_control._expand_pointer, ">> ")
        self.assertEqual(
            content_control.choices,
            [
                {"name": "---------------", "value": ANY, "enabled": False},
                {"key": "b", "name": "hello", "value": "world", "enabled": False},
                {"name": "**********", "value": ANY, "enabled": False},
                {"key": "f", "name": "foo", "value": "boo", "enabled": False},
                {
                    "key": "h",
                    "name": "(haha)",
                    "value": ExpandHelp(help_msg="(haha)"),
                    "enabled": False,
                },
            ],
        )
        self.assertIsInstance(content_control.choices[0]["value"], Separator)

        self.assertEqual(
            content_control._get_formatted_choices(),
            [("class:pointer", ">> "), ("", "foo")],
        )
        self.assertEqual(
            content_control._get_hover_text(content_control.choices[1]),
            [
                ("class:pointer", " "),
                ("class:marker", " "),
                ("class:pointer", "b) "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "hello"),
            ],
        )
        self.assertEqual(
            content_control._get_normal_text(content_control.choices[1]),
            [("", " "), ("class:marker", " "), ("", "b) "), ("", "hello")],
        )

    def test_content_control_exceptions(self):
        self.assertRaises(
            InvalidArgument,
            InquirerPyExpandControl,
            ["asdfasfd", {"name": "hello", "value": "hello", "key": "j"}],
            "f",
            "",
            "",
            "",
            "",
            "",
        )

        self.assertRaises(
            RequiredKeyNotFound,
            InquirerPyExpandControl,
            [
                {"name": "foo", "value": "boo"},
                {"name": "hello", "value": "hello", "key": "j"},
            ],
            "f",
            "",
            "",
            "",
            "",
            "",
        )

    def test_prompt(self):
        prompt = ExpandPrompt(
            message="Choose one of the following",
            default="boo",
            choices=self.choices,
            editing_mode="vim",
            help_msg="What",
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        self.assertEqual(prompt.instruction, "(bfh)")
        prompt._instruction = "hello"
        self.assertEqual(prompt.instruction, "hello")

    @patch.object(KeyBindings, "add")
    def test_kb_added(self, mocked_add):
        ExpandPrompt(
            message="hello",
            choices=self.choices,
        )
        mocked_add.assert_has_calls([call("b", filter=True)])
        mocked_add.assert_has_calls([call("f", filter=True)])
        mocked_add.assert_has_calls([call("h", filter=True)])

    def test_prompt_message(self):
        prompt = ExpandPrompt(message="Choose one", choices=self.choices)
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Choose one"),
                ("class:instruction", " (bfh)"),
                ("class:input", " b"),
            ],
        )

        prompt = ExpandPrompt(message="Choose one", choices=self.choices, default="f")
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Choose one"),
                ("class:instruction", " (bfh)"),
                ("class:input", " f"),
            ],
        )
        prompt._handle_up()
        prompt._handle_up()
        prompt._handle_down()
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Choose one"),
                ("class:instruction", " (bfh)"),
                ("class:input", " f"),
            ],
        )
        prompt.content_control._expanded = True
        prompt._handle_down()
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Choose one"),
                ("class:instruction", " (bfh)"),
                ("class:input", " b"),
            ],
        )

        prompt.status["result"] = "foo"
        prompt.status["answered"] = True
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Choose one"),
                ("class:answer", " foo"),
            ],
        )

    def test_bindings(self):
        prompt = ExpandPrompt(message="Choose one", choices=self.choices)
        prompt.content_control._expanded = True
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 3)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"result": "foo", "answered": True})

    def test_key_not_expand(self):
        prompt = ExpandPrompt(message="", choices=self.choices)
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": False, "key": "b", "name": "hello", "value": "world"},
                {"enabled": False, "name": "**********", "value": ANY},
                {"enabled": False, "key": "f", "name": "foo", "value": "boo"},
                {
                    "enabled": False,
                    "key": "h",
                    "name": "Help, list all choices",
                    "value": ExpandHelp(help_msg="Help, list all choices"),
                },
            ],
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._toggle_choice()
        self.assertEqual(
            prompt.content_control.selection,
            {"enabled": False, "key": "b", "name": "hello", "value": "world"},
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": False, "key": "b", "name": "hello", "value": "world"},
                {"enabled": False, "name": "**********", "value": ANY},
                {"enabled": False, "key": "f", "name": "foo", "value": "boo"},
                {
                    "enabled": False,
                    "key": "h",
                    "name": "Help, list all choices",
                    "value": ExpandHelp(help_msg="Help, list all choices"),
                },
            ],
        )

    def test_key_expand(self):
        prompt = ExpandPrompt(message="", choices=self.choices)
        prompt.content_control._expanded = True
        prompt._toggle_choice()
        self.assertEqual(
            prompt.content_control.selection,
            {"enabled": True, "key": "b", "name": "hello", "value": "world"},
        )
        prompt._toggle_choice()
        self.assertEqual(
            prompt.content_control.selection,
            {"enabled": False, "key": "b", "name": "hello", "value": "world"},
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": True, "key": "b", "name": "hello", "value": "world"},
                {"enabled": False, "name": "**********", "value": ANY},
                {"enabled": True, "key": "f", "name": "foo", "value": "boo"},
                {
                    "enabled": False,
                    "key": "h",
                    "name": "Help, list all choices",
                    "value": ExpandHelp(help_msg="Help, list all choices"),
                },
            ],
        )
        prompt._toggle_all(True)
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "name": "---------------", "value": ANY},
                {"enabled": False, "key": "b", "name": "hello", "value": "world"},
                {"enabled": False, "name": "**********", "value": ANY},
                {"enabled": False, "key": "f", "name": "foo", "value": "boo"},
                {
                    "enabled": False,
                    "key": "h",
                    "name": "Help, list all choices",
                    "value": ExpandHelp(help_msg="Help, list all choices"),
                },
            ],
        )
