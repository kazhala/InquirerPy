import unittest

from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.prompts.fuzzy.fuzzy import FuzzyPrompt, InquirerPyFuzzyControl


class TestFuzzy(unittest.TestCase):
    content_control = InquirerPyFuzzyControl(
        choices=["haah", "haha", "what", "waht", "weaht"],
        default="what",
        pointer=INQUIRERPY_POINTER_SEQUENCE,
        marker=INQUIRERPY_POINTER_SEQUENCE,
        current_text=lambda: "yes",
    )

    def test_content_control_init(self):
        self.assertEqual(self.content_control._pointer, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(self.content_control._marker, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(self.content_control._current_text(), "yes")
        self.assertEqual(
            self.content_control.choices,
            [
                {"index": 0, "name": "haah", "selected": False, "value": "haah"},
                {"index": 1, "name": "haha", "selected": False, "value": "haha"},
                {"index": 2, "name": "what", "selected": False, "value": "what"},
                {"index": 3, "name": "waht", "selected": False, "value": "waht"},
                {"index": 4, "name": "weaht", "selected": False, "value": "weaht"},
            ],
        )
        self.assertEqual(
            self.content_control._filtered_choices,
            [
                {"index": 0, "name": "haah", "selected": False, "value": "haah"},
                {"index": 1, "name": "haha", "selected": False, "value": "haha"},
                {"index": 2, "name": "what", "selected": False, "value": "what"},
                {"index": 3, "name": "waht", "selected": False, "value": "waht"},
                {"index": 4, "name": "weaht", "selected": False, "value": "weaht"},
            ],
        )
        self.assertEqual(self.content_control._filtered_indices, [])
        self.assertEqual(self.content_control.selected_choice_index, 2)
        self.assertEqual(
            self.content_control.selection,
            {"index": 2, "name": "what", "selected": False, "value": "what"},
        )
        self.assertEqual(self.content_control.choice_count, 5)

    def test_content_control_text(self):
        self.content_control.choices[0]["selected"] = True
        self.assertEqual(
            self.content_control._get_formatted_choices(),
            [
                ("class:pointer", " "),
                ("class:fuzzy_marker", "❯"),
                ("", "haah"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:fuzzy_marker", " "),
                ("", "haha"),
                ("", "\n"),
                ("class:pointer", "❯"),
                ("class:fuzzy_marker", " "),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "what"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:fuzzy_marker", " "),
                ("", "waht"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:fuzzy_marker", " "),
                ("", "weaht"),
            ],
        )
        self.content_control.choices[0]["selected"] = False

    def test_content_control_filter(self):
        content_control = InquirerPyFuzzyControl(
            choices=["meat", "what", "whaaah", "weather", "haha"],
            default="what",
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            current_text=lambda: "wh",
        )
        self.assertEqual(
            content_control._filtered_choices,
            [
                {"index": 0, "name": "meat", "selected": False, "value": "meat"},
                {"index": 1, "name": "what", "selected": False, "value": "what"},
                {"index": 2, "name": "whaaah", "selected": False, "value": "whaaah"},
                {"index": 3, "name": "weather", "selected": False, "value": "weather"},
                {"index": 4, "name": "haha", "selected": False, "value": "haha"},
            ],
        )
        self.assertEqual(content_control._filtered_indices, [])
        content_control.filter_choices()
        self.assertEqual(
            content_control._filtered_choices,
            [
                {"index": 1, "name": "what", "selected": False, "value": "what"},
                {"index": 2, "name": "whaaah", "selected": False, "value": "whaaah"},
                {"index": 3, "name": "weather", "selected": False, "value": "weather"},
            ],
        )
        self.assertEqual(content_control._filtered_indices, [[0, 1], [0, 1], [0, 4]])
        self.assertEqual(
            content_control._get_formatted_choices(),
            [
                ("class:pointer", " "),
                ("class:fuzzy_marker", " "),
                ("class:fuzzy_match", "w"),
                ("class:fuzzy_match", "h"),
                ("", "a"),
                ("", "t"),
                ("", "\n"),
                ("class:pointer", "❯"),
                ("class:fuzzy_marker", " "),
                ("[SetCursorPosition]", ""),
                ("class:fuzzy_match", "w"),
                ("class:fuzzy_match", "h"),
                ("class:pointer", "a"),
                ("class:pointer", "a"),
                ("class:pointer", "a"),
                ("class:pointer", "h"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:fuzzy_marker", " "),
                ("class:fuzzy_match", "w"),
                ("", "e"),
                ("", "a"),
                ("", "t"),
                ("class:fuzzy_match", "h"),
                ("", "e"),
                ("", "r"),
            ],
        )
        self.assertEqual(content_control.choice_count, 3)
