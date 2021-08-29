import inspect
import os
import unittest
from unittest.mock import PropertyMock, patch

from prompt_toolkit.application.application import Application

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.utils import (
    InquirerPyStyle,
    calculate_height,
    color_print,
    get_style,
    transform_async,
)

from .style import get_sample_style


class TestUtils(unittest.TestCase):
    @patch("InquirerPy.utils.shutil.get_terminal_size")
    def test_prompt_height(self, mocked_terminal_size):
        mocked_terminal_size.return_value = (24, 80)
        height, max_height = calculate_height(None, None)
        self.assertEqual(height, None)
        self.assertEqual(max_height, 54)

        height, max_height = calculate_height("50%", None)
        self.assertEqual(height, 38)
        self.assertEqual(max_height, 78)

        calculate_height("50%", "80")

        self.assertRaises(InvalidArgument, calculate_height, "adsfa", "40%")
        self.assertRaises(InvalidArgument, calculate_height, "50%", "asfasdds")

        height, max_height = calculate_height(None, "80%")
        self.assertEqual(height, None)
        self.assertEqual(max_height, 62)

        height, max_height = calculate_height("1%", None)
        self.assertEqual(height, 1)

    def test_style(self):
        style = get_style()
        self.assertEqual(
            style,
            InquirerPyStyle(get_sample_style()),
        )

        os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = "#000000"
        os.environ["INQUIRERPY_STYLE_ANSWERMARK"] = "#000000"
        os.environ["INQUIRERPY_STYLE_ANSWER"] = "#111111"
        os.environ["INQUIRERPY_STYLE_QUESTION"] = "#222222"
        os.environ["INQUIRERPY_STYLE_ANSWERED_QUESTION"] = "#222222"
        os.environ["INQUIRERPY_STYLE_INSTRUCTION"] = "#333333"
        os.environ["INQUIRERPY_STYLE_INPUT"] = "#444444"
        os.environ["INQUIRERPY_STYLE_POINTER"] = "#555555"
        os.environ["INQUIRERPY_STYLE_CHECKBOX"] = "#66666"
        os.environ["INQUIRERPY_STYLE_SEPARATOR"] = "#777777"
        os.environ["INQUIRERPY_STYLE_SKIPPED"] = "#888888"
        os.environ["INQUIRERPY_STYLE_FUZZY_PROMPT"] = "#999999"
        os.environ["INQUIRERPY_STYLE_FUZZY_INFO"] = "#aaaaaa"
        os.environ["INQUIRERPY_STYLE_MARKER"] = "#bbbbbb"
        os.environ["INQUIRERPY_STYLE_FUZZY_BORDER"] = "#cccccc"
        os.environ["INQUIRERPY_STYLE_FUZZY_MATCH"] = "#dddddd"
        os.environ["INQUIRERPY_STYLE_VALIDATOR"] = "#dddddd"
        os.environ["INQUIRERPY_STYLE_SPINNER_PATTERN"] = "#ssssss"
        os.environ["INQUIRERPY_STYLE_SPINNER_TEXT"] = "#llllll"
        style = get_style()
        self.assertEqual(
            style,
            InquirerPyStyle(
                {
                    "questionmark": "#000000",
                    "answermark": "#000000",
                    "answer": "#111111",
                    "input": "#444444",
                    "question": "#222222",
                    "answered_question": "#222222",
                    "instruction": "#333333",
                    "pointer": "#555555",
                    "checkbox": "#66666",
                    "separator": "#777777",
                    "skipped": "#888888",
                    "fuzzy_prompt": "#999999",
                    "fuzzy_info": "#aaaaaa",
                    "marker": "#bbbbbb",
                    "validation-toolbar": "#dddddd",
                    "fuzzy_match": "#dddddd",
                    "frame.border": "#cccccc",
                    "spinner_pattern": "#ssssss",
                    "spinner_text": "#llllll",
                },
            ),
        )

    def test_format_style(self):
        raw = {
            "questionmark": "#000000",
            "answermark": "#mmmmmm",
            "answer": "#111111",
            "input": "#444444",
            "question": "#222222",
            "answered_question": "#222222",
            "instruction": "#333333",
            "pointer": "#555555",
            "checkbox": "#66666",
            "separator": "#777777",
            "skipped": "#888888",
            "fuzzy_prompt": "#999999",
            "fuzzy_info": "#aaaaaa",
            "marker": "#bbbbbb",
            "validator": "#dddddd",
            "fuzzy_match": "#dddddd",
            "fuzzy_border": "#cccccc",
            "spinner_pattern": "#ssssss",
            "spinner_text": "#llllll",
        }
        style = get_style(raw)
        raw["frame.border"] = raw.pop("fuzzy_border")
        raw["validation-toolbar"] = raw.pop("validator")
        self.assertEqual(
            style,
            InquirerPyStyle(raw),
        )

    @patch("InquirerPy.utils.print_formatted_text")
    @patch("InquirerPy.utils.run_in_terminal")
    @patch.object(Application, "is_running", new_callable=PropertyMock)
    def test_color_print(self, mocked_running, mocked_term, mocked_print):
        mocked_running.return_value = True
        color_print([("class:aa", "haha")], style={"aa": "#ffffff"})
        mocked_term.assert_called_once()

        mocked_term.reset_mock()
        mocked_running.return_value = False
        color_print([("class:aa", "haha")], style={"aa": "#ffffff"})
        mocked_term.assert_not_called()
        mocked_print.assert_called_once()

    def test_transform_async(self):
        def hello():
            pass

        self.assertFalse(inspect.iscoroutinefunction(hello))

        self.assertTrue(inspect.iscoroutinefunction(transform_async(hello)))
