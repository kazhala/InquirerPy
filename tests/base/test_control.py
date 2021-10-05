import asyncio
import unittest

from InquirerPy.base.control import Choice
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.prompts.list import InquirerPyListControl
from InquirerPy.separator import Separator


class TestBaseControl(unittest.TestCase):
    def test_constructor(self) -> None:
        control = InquirerPyListControl(
            choices=[1, 2, 3],
            default=None,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control._default, None)
        self.assertEqual(
            control.choices,
            [
                {"name": "1", "value": 1, "enabled": False},
                {"name": "2", "value": 2, "enabled": False},
                {"name": "3", "value": 3, "enabled": False},
            ],
        )
        self.assertFalse(control._loading)
        self.assertEqual(control._choice_func, None)

    def test_constructor_choice_callable(self):
        control = InquirerPyListControl(
            choices=lambda _: [1, 2, 3],
            default=lambda _: 1,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control._default, 1)
        self.assertNotEqual(control._choice_func, None)
        self.assertTrue(control._loading)
        self.assertEqual(control.choices, [])

    def test_retrieve_choices(self) -> None:
        control = InquirerPyListControl(
            choices=lambda _: [1, 2, 3],
            default=lambda _: 1,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.choices, [])
        self.assertTrue(control._loading)
        asyncio.run(control.retrieve_choices())
        self.assertEqual(
            control.choices,
            [
                {"name": "1", "value": 1, "enabled": False},
                {"name": "2", "value": 2, "enabled": False},
                {"name": "3", "value": 3, "enabled": False},
            ],
        )
        self.assertFalse(control._loading)

    def test_get_choices_list(self):
        sep = Separator()
        choice = [1, 2, 3, sep]
        default = 2
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.selected_choice_index, 1)
        choices = control._get_choices(choice, 1)
        self.assertEqual(
            choices,
            [
                {"name": "1", "value": 1, "enabled": False},
                {"name": "2", "value": 2, "enabled": False},
                {"name": "3", "value": 3, "enabled": False},
                {"enabled": False, "name": "---------------", "value": sep},
            ],
        )
        self.assertEqual(control.selected_choice_index, 0)

    def test_get_choices_dict(self):
        sep = Separator()
        choice = [
            {"name": "1", "value": 1, "enabled": True},
            {"name": "2", "value": 2, "enabled": True},
            {"name": "3", "value": 3, "enabled": True},
            sep,
        ]
        default = 2
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.selected_choice_index, 1)
        choices = control._get_choices(choice, 1)
        self.assertEqual(
            choices,
            [
                {"name": "1", "value": 1, "enabled": False},
                {"name": "2", "value": 2, "enabled": False},
                {"name": "3", "value": 3, "enabled": False},
                {"enabled": False, "name": "---------------", "value": sep},
            ],
        )
        self.assertEqual(control.selected_choice_index, 0)

        control._multiselect = True
        choices = control._get_choices(choice, 1)
        self.assertEqual(
            choices,
            [
                {"name": "1", "value": 1, "enabled": True},
                {"name": "2", "value": 2, "enabled": True},
                {"name": "3", "value": 3, "enabled": True},
                {"enabled": False, "name": "---------------", "value": sep},
            ],
        )

    def test_get_choices_key_error(self):
        choice = [
            {"asdf": "1", "value": 1, "enabled": True},
            {"name": "2", "value": 2, "enabled": True},
            {"name": "3", "value": 3, "enabled": True},
        ]
        control = InquirerPyListControl(
            choices=[1],
            default=None,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertRaises(RequiredKeyNotFound, control._get_choices, choice, None)

    def test_safety_check(self):
        control = InquirerPyListControl(
            choices=[1],
            default=None,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        control._choices = []
        self.assertRaises(InvalidArgument, control._safety_check)

        control._choices = control._get_choices([Separator(), Separator()], None)
        self.assertRaises(InvalidArgument, control._safety_check)

    def test_get_formatted_choices(self):
        list_control = InquirerPyListControl(
            [
                {"name": "apple", "value": "peach"},
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

    def test_choice_count(self):
        choice = [
            {"name": "1", "value": 1, "enabled": True},
            {"name": "2", "value": 2, "enabled": True},
            {"name": "3", "value": 3, "enabled": True},
        ]
        default = 2
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.choice_count, 3)

    def test_selection(self):
        choice = [
            {"name": "1", "value": 1, "enabled": True},
            {"name": "2", "value": 2, "enabled": True},
            {"name": "3", "value": 3, "enabled": True},
        ]
        default = 2
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.selection, {"name": "2", "value": 2, "enabled": False})

    def test_choice(self):
        choice = [Choice(1), Choice(2), Choice(3, None, True)]

        default = 2
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=False,
            marker_pl=" ",
        )
        self.assertEqual(control.selection, {"name": "2", "value": 2, "enabled": False})
        self.assertEqual(
            control.choices,
            [
                {"enabled": False, "name": "1", "value": 1},
                {"enabled": False, "name": "2", "value": 2},
                {"enabled": False, "name": "3", "value": 3},
            ],
        )

    def test_choice_multi(self):
        choice = [Choice(1), Choice(2), Choice(3, None, True)]

        default = 4
        control = InquirerPyListControl(
            choices=choice,
            default=default,
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            session_result=None,
            multiselect=True,
            marker_pl=" ",
        )
        self.assertEqual(control.selection, {"name": "1", "value": 1, "enabled": False})
        self.assertEqual(
            control.choices,
            [
                {"enabled": False, "name": "1", "value": 1},
                {"enabled": False, "name": "2", "value": 2},
                {"enabled": True, "name": "3", "value": 3},
            ],
        )
