import asyncio
import unittest
from unittest.mock import patch

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.layout import Layout

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

    def setUp(self):
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
                {"index": 0, "name": "haah", "enabled": False, "value": "haah"},
                {"index": 1, "name": "haha", "enabled": False, "value": "haha"},
                {"index": 2, "name": "what", "enabled": False, "value": "what"},
                {"index": 3, "name": "waht", "enabled": False, "value": "waht"},
                {"index": 4, "name": "weaht", "enabled": False, "value": "weaht"},
            ],
        )
        self.assertEqual(
            self.content_control._filtered_choices,
            [
                {"index": 0, "name": "haah", "enabled": False, "value": "haah"},
                {"index": 1, "name": "haha", "enabled": False, "value": "haha"},
                {"index": 2, "name": "what", "enabled": False, "value": "what"},
                {"index": 3, "name": "waht", "enabled": False, "value": "waht"},
                {"index": 4, "name": "weaht", "enabled": False, "value": "weaht"},
            ],
        )
        self.assertEqual(self.content_control._filtered_indices, [])
        self.assertEqual(self.content_control.selected_choice_index, 2)
        self.assertEqual(
            self.content_control.selection,
            {"index": 2, "name": "what", "enabled": False, "value": "what"},
        )
        self.assertEqual(self.content_control.choice_count, 5)

    def test_content_control_text(self):
        self.content_control.choices[0]["enabled"] = True
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
        self.content_control.choices[0]["enabled"] = False

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
                {"index": 0, "name": "meat", "enabled": False, "value": "meat"},
                {"index": 1, "name": "what", "enabled": False, "value": "what"},
                {"index": 2, "name": "whaaah", "enabled": False, "value": "whaaah"},
                {"index": 3, "name": "weather", "enabled": False, "value": "weather"},
                {"index": 4, "name": "haha", "enabled": False, "value": "haha"},
            ],
        )
        self.assertEqual(content_control._filtered_indices, [])
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            loop.create_task(content_control.filter_choices())
        else:
            asyncio.run(content_control.filter_choices())

        self.assertEqual(
            content_control._filtered_choices,
            [
                {"index": 1, "name": "what", "enabled": False, "value": "what"},
                {"index": 2, "name": "whaaah", "enabled": False, "value": "whaaah"},
                {"index": 3, "name": "weather", "enabled": False, "value": "weather"},
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

    def test_prompt_after_input(self):
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

    def test_prompt_before_input(self):
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
                {"index": 0, "name": "haah", "enabled": False, "value": "haah"},
                {"index": 1, "name": "haha", "enabled": False, "value": "haha"},
                {"index": 2, "name": "what", "enabled": False, "value": "what"},
            ],
        )
        self.assertEqual(self.prompt.content_control.selected_choice_index, 2)
        self.prompt._buffer.text = ""
        self.prompt._on_text_changed(None)
        self.assertEqual(self.prompt.content_control.selected_choice_index, 2)
        self.assertEqual(
            self.prompt.content_control._filtered_choices,
            [
                {"index": 0, "name": "haah", "enabled": False, "value": "haah"},
                {"index": 1, "name": "haha", "enabled": False, "value": "haha"},
                {"index": 2, "name": "what", "enabled": False, "value": "what"},
                {"index": 3, "name": "waht", "enabled": False, "value": "waht"},
                {"index": 4, "name": "weaht", "enabled": False, "value": "weaht"},
            ],
        )
        self.prompt.content_control.selected_choice_index = 0

    def test_prompt_bindings(self):
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.prompt._handle_down()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 1)
        self.prompt._handle_down()
        self.prompt._handle_down()
        self.prompt._handle_down()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 4)
        self.prompt._handle_down()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.prompt._handle_up()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 4)
        self.prompt._handle_up()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 3)
        self.prompt._handle_up()
        self.prompt._handle_up()
        self.prompt._handle_up()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.prompt._handle_enter(event)
        self.assertEqual(self.prompt.status, {"answered": True, "result": "haah"})

        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
            multiselect=True,
        )
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"answered": True, "result": ["haah"]})
        prompt.status = {"answered": False, "result": None}
        prompt._handle_tab()
        prompt._handle_down()
        prompt._handle_tab()
        prompt._handle_down()
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"answered": True, "result": ["haah", "haha"]})

        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=["haah", "haha", "what", "waht", "weaht"],
            multiselect=True,
        )
        prompt._buffer.text = "asdfasfasfasfad"
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertEqual(prompt.status, {"answered": True, "result": []})

    def test_prompt_message(self):
        self.assertEqual(
            self.prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one of them"),
                ("class:instruction", " "),
            ],
        )
        self.prompt.status = {"answered": True, "result": ["hello"]}
        self.assertEqual(
            self.prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one of them"),
                ("class:answer", " ['hello']"),
            ],
        )

    def test_prompt_validator(self):
        prompt = FuzzyPrompt(
            message="Select one",
            choices=["haha", "asa", "132132"],
            validate=lambda x: len(x) > 1,
            invalid_message="what",
            multiselect=True,
        )
        self.assertEqual(prompt._invalid, False)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
            self.assertEqual(prompt._invalid_message, "what")
            self.assertEqual(prompt._invalid, True)

        prompt._on_text_changed("")
        self.assertEqual(prompt._invalid, False)

    def test_prompt_toggle(self):
        prompt = FuzzyPrompt(message="", choices=["haha", "asdfa", "112321fd"])
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "index": 0, "name": "haha", "value": "haha"},
                {"enabled": False, "index": 1, "name": "asdfa", "value": "asdfa"},
                {"enabled": False, "index": 2, "name": "112321fd", "value": "112321fd"},
            ],
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": True, "index": 0, "name": "haha", "value": "haha"},
                {"enabled": True, "index": 1, "name": "asdfa", "value": "asdfa"},
                {"enabled": True, "index": 2, "name": "112321fd", "value": "112321fd"},
            ],
        )
        prompt._toggle_all(True)
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": True, "index": 0, "name": "haha", "value": "haha"},
                {"enabled": True, "index": 1, "name": "asdfa", "value": "asdfa"},
                {"enabled": True, "index": 2, "name": "112321fd", "value": "112321fd"},
            ],
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "index": 0, "name": "haha", "value": "haha"},
                {"enabled": False, "index": 1, "name": "asdfa", "value": "asdfa"},
                {"enabled": False, "index": 2, "name": "112321fd", "value": "112321fd"},
            ],
        )
