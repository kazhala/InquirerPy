import unittest
from unittest.mock import patch

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.layout import Layout

from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.fuzzy.fuzzy import FuzzyPrompt, InquirerPyFuzzyControl


class TestFuzzy(unittest.TestCase):
    content_control = InquirerPyFuzzyControl(
        choices=["haah", "haha", "what", "waht", "weaht"],
        default="what",
        pointer=INQUIRERPY_POINTER_SEQUENCE,
        marker=INQUIRERPY_POINTER_SEQUENCE,
        current_text=lambda: "yes",
    )

    @patch.object(FuzzyPrompt, "_get_height")
    def setUp(self, mocked_height):
        mocked_height.return_value = (10, 20)
        self.prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
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

    def test_prompt_init(self):
        self.assertEqual(self.prompt._instruction, "")
        self.assertEqual(self.prompt._multiselect, False)
        self.assertEqual(self.prompt._prompt, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(self.prompt._border, True)
        self.assertEqual(self.prompt._info, True)
        self.assertIsInstance(self.prompt._buffer, Buffer)
        self.assertIsInstance(self.prompt._layout, Layout)
        self.assertIsInstance(self.prompt._application, Application)

    @patch("InquirerPy.prompts.fuzzy.fuzzy.shutil.get_terminal_size")
    def test_prompt_height(self, mocked_terminal_size):
        mocked_terminal_size.return_value = (24, 80)
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
        )
        height, max_height = prompt._get_height(None, None)
        self.assertEqual(height, None)
        self.assertEqual(max_height, 78)

        height, max_height = prompt._get_height("50%", None)
        self.assertEqual(height, 38)
        self.assertEqual(max_height, 78)

        prompt._get_height("50%", "80")

        self.assertRaises(InvalidArgument, prompt._get_height, "50%", "40%")
        self.assertRaises(InvalidArgument, prompt._get_height, "50", "40%")
        self.assertRaises(InvalidArgument, prompt._get_height, "adsfa", "40%")
        self.assertRaises(InvalidArgument, prompt._get_height, "50%", "asfasdds")

        height, max_height = prompt._get_height(None, "80%")
        self.assertEqual(height, None)
        self.assertEqual(max_height, 64)

    @patch.object(FuzzyPrompt, "_get_height")
    def test_prompt_after_input(self, mocked_height):
        mocked_height.return_value = (10, 20)
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
        )
        self.assertEqual(
            prompt._generate_after_input(), [("", "  "), ("class:fuzzy_info", "5/5")]
        )
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
            info=False,
        )
        self.assertEqual(prompt._generate_after_input(), [])

    @patch.object(FuzzyPrompt, "_get_height")
    def test_prompt_before_input(self, mocked_height):
        mocked_height.return_value = (10, 20)
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
        )
        self.assertEqual(
            prompt._generate_before_input(), [("class:fuzzy_prompt", "❯ ")]
        )
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
            prompt=">",
        )
        self.assertEqual(
            prompt._generate_before_input(), [("class:fuzzy_prompt", "> ")]
        )

    def test_prompt_on_text_changed(self):
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.prompt.content_control.selected_choice_index = 4
        self.prompt._buffer.text = "ha"
        self.prompt._on_text_changed(None)
        self.assertEqual(
            self.prompt.content_control._filtered_choices,
            [
                {"index": 0, "name": "haah", "selected": False, "value": "haah"},
                {"index": 1, "name": "haha", "selected": False, "value": "haha"},
                {"index": 2, "name": "what", "selected": False, "value": "what"},
            ],
        )
        self.assertEqual(self.prompt.content_control.selected_choice_index, 2)
