import asyncio
import unittest
from typing import Callable, NamedTuple
from unittest.mock import MagicMock, PropertyMock, patch

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.layout import Layout

from InquirerPy.base.complex import BaseComplexPrompt
from InquirerPy.base.control import InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.prompts.fuzzy.fuzzy import FuzzyPrompt, InquirerPyFuzzyControl
from InquirerPy.spinner import SpinnerWindow


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestFuzzy(unittest.TestCase):
    content_control = InquirerPyFuzzyControl(
        choices=["haah", "haha", "what", "waht", "weaht"],
        pointer=INQUIRERPY_POINTER_SEQUENCE,
        marker=INQUIRERPY_POINTER_SEQUENCE,
        current_text=lambda: "yes",
        max_lines=80,
        session_result=None,
        multiselect=False,
    )

    @patch("InquirerPy.utils.shutil.get_terminal_size")
    def setUp(self, mocked_term):
        mocked_term.return_value = (24, 80)
        self.prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
        )

    def test_content_control_init(self):
        self.assertEqual(self.content_control._pointer, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(self.content_control._marker, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(self.content_control._current_text(), "yes")
        self.assertEqual(
            self.content_control.choices,
            [
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "haah",
                    "value": "haah",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "what",
                    "value": "what",
                },
                {
                    "enabled": False,
                    "index": 3,
                    "indices": [],
                    "name": "waht",
                    "value": "waht",
                },
                {
                    "enabled": False,
                    "index": 4,
                    "indices": [],
                    "name": "weaht",
                    "value": "weaht",
                },
            ],
        )
        self.assertEqual(
            self.content_control._filtered_choices,
            [
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "haah",
                    "value": "haah",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "what",
                    "value": "what",
                },
                {
                    "enabled": False,
                    "index": 3,
                    "indices": [],
                    "name": "waht",
                    "value": "waht",
                },
                {
                    "enabled": False,
                    "index": 4,
                    "indices": [],
                    "name": "weaht",
                    "value": "weaht",
                },
            ],
        )
        self.assertEqual(self.content_control.selected_choice_index, 0)
        self.assertEqual(
            self.content_control.selection,
            {
                "index": 0,
                "name": "haah",
                "enabled": False,
                "value": "haah",
                "indices": [],
            },
        )
        self.assertEqual(self.content_control.choice_count, 5)

    def test_content_control_text(self):
        self.content_control.choices[0]["enabled"] = True
        self.assertEqual(
            self.content_control._get_formatted_choices(),
            [
                ("class:pointer", "❯"),
                ("class:marker", "❯"),
                ("[SetCursorPosition]", ""),
                ("class:pointer", "haah"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("", "haha"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("", "what"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("", "waht"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("", "weaht"),
            ],
        )
        self.content_control.choices[0]["enabled"] = False

    def test_prompt_filter1(self):
        content_control = InquirerPyFuzzyControl(
            choices=["meat", "what", "whaaah", "weather", "haha"],
            pointer=INQUIRERPY_POINTER_SEQUENCE,
            marker=INQUIRERPY_POINTER_SEQUENCE,
            current_text=lambda: "wh",
            max_lines=80,
            session_result=None,
            multiselect=False,
        )
        self.assertEqual(
            content_control._filtered_choices,
            [
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "meat",
                    "value": "meat",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "what",
                    "value": "what",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "whaaah",
                    "value": "whaaah",
                },
                {
                    "enabled": False,
                    "index": 3,
                    "indices": [],
                    "name": "weather",
                    "value": "weather",
                },
                {
                    "enabled": False,
                    "index": 4,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
            ],
        )
        result = asyncio.run(content_control._filter_choices(0.0))
        self.assertEqual(
            result,
            [
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [0, 1],
                    "name": "what",
                    "value": "what",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [0, 1],
                    "name": "whaaah",
                    "value": "whaaah",
                },
                {
                    "enabled": False,
                    "index": 3,
                    "indices": [0, 4],
                    "name": "weather",
                    "value": "weather",
                },
            ],
        )
        content_control._filtered_choices = result
        self.assertEqual(
            content_control._get_formatted_choices(),
            [
                ("class:pointer", "❯"),
                ("class:marker", " "),
                ("[SetCursorPosition]", ""),
                ("class:fuzzy_match", "w"),
                ("class:fuzzy_match", "h"),
                ("class:pointer", "a"),
                ("class:pointer", "t"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
                ("class:fuzzy_match", "w"),
                ("class:fuzzy_match", "h"),
                ("", "a"),
                ("", "a"),
                ("", "a"),
                ("", "h"),
                ("", "\n"),
                ("class:pointer", " "),
                ("class:marker", " "),
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
        self.assertEqual(content_control.selected_choice_index, 0)

    @patch("InquirerPy.prompts.fuzzy.fuzzy.calculate_height")
    @patch("InquirerPy.utils.shutil.get_terminal_size")
    def test_prompt_init(self, mocked_term, mocked_height):
        mocked_term.return_value = (24, 80)
        mocked_height.return_value = (24, 80)
        message = 15 * "i"
        qmark = "[?]"
        instruction = 2 * "i"
        prompt = FuzzyPrompt(
            message=message,
            qmark=qmark,
            instruction=instruction,
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
        )

        self.assertEqual(prompt._instruction, instruction)
        self.assertEqual(prompt._multiselect, False)
        self.assertEqual(prompt._prompt, INQUIRERPY_POINTER_SEQUENCE)
        self.assertEqual(prompt._border, True)
        self.assertEqual(prompt._info, True)
        self.assertIsInstance(prompt._buffer, Buffer)
        self.assertIsInstance(prompt._layout, Layout)
        self.assertIsInstance(prompt._application, Application)
        mocked_height.assert_called_with(
            None,
            None,
            offset=3,
            wrap_lines_offset=(len(qmark) + 1 + len(message) + 1 + len(instruction) + 1)
            // 24,
        )

        instruction = 3 * "i"
        prompt = FuzzyPrompt(
            message=message,
            qmark=qmark,
            instruction=instruction,
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
        )
        mocked_height.assert_called_with(
            None,
            None,
            offset=3,
            wrap_lines_offset=(len(qmark) + 1 + len(message) + 1 + len(instruction) + 1)
            // 24,
        )

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

    @patch("asyncio.create_task")
    def test_prompt_on_text_changed(self, mocked):
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.prompt.content_control.selected_choice_index = 4
        self.prompt._buffer.text = "ha"
        mocked.assert_called()

    def test_prompt_filter_callback(self):
        class Hello(NamedTuple):
            cancelled: Callable
            result: Callable

        hello = Hello(cancelled=lambda: True, result=lambda: [])
        self.prompt._filter_callback(hello)
        self.assertEqual(
            self.prompt.content_control._filtered_choices,
            [
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "haah",
                    "value": "haah",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "what",
                    "value": "what",
                },
                {
                    "enabled": False,
                    "index": 3,
                    "indices": [],
                    "name": "waht",
                    "value": "waht",
                },
                {
                    "enabled": False,
                    "index": 4,
                    "indices": [],
                    "name": "weaht",
                    "value": "weaht",
                },
            ],
        )
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.prompt.content_control.selected_choice_index = 4
        hello = Hello(cancelled=lambda: False, result=lambda: [])
        self.prompt._filter_callback(hello)
        self.prompt.content_control._get_formatted_choices()
        self.assertEqual(self.prompt.content_control._filtered_choices, [])
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)

        self.prompt.content_control.selected_choice_index = -1
        hello = Hello(
            cancelled=lambda: False,
            result=lambda: [
                {
                    "enabled": False,
                    "index": i,
                    "indices": [],
                    "name": "weaht",
                    "value": "weaht",
                }
                for i in range(3)
            ],
        )
        self.prompt._filter_callback(hello)
        self.prompt.content_control._get_formatted_choices()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 0)
        self.assertEqual(self.prompt.content_control._first_line, 0)
        self.assertEqual(self.prompt.content_control._last_line, 3)

        self.prompt.content_control.selected_choice_index = 5
        hello = Hello(
            cancelled=lambda: False,
            result=lambda: [
                {
                    "enabled": False,
                    "index": i,
                    "indices": [],
                    "name": "weaht",
                    "value": "weaht",
                }
                for i in range(3)
            ],
        )
        self.prompt._filter_callback(hello)
        self.prompt.content_control._get_formatted_choices()
        self.assertEqual(self.prompt.content_control.selected_choice_index, 2)
        self.assertEqual(self.prompt.content_control._first_line, 0)
        self.assertEqual(self.prompt.content_control._last_line, 3)

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
        prompt._toggle_choice()
        prompt._handle_down()
        prompt._toggle_choice()
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
        prompt.content_control._filtered_choices = []
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
                ("class:answermark", "?"),
                ("class:answered_question", " Select one of them"),
                ("class:answer", " ['hello']"),
            ],
        )

        prompt = FuzzyPrompt(
            message=lambda result: "no" if not result else "hello",
            choices=[1, 2, 3],
            session_result={"1": True},
        )
        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " hello"),
                ("class:instruction", " "),
            ],
        )

    @patch("asyncio.create_task")
    def test_prompt_validator(self, mocked):
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
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "asdfa",
                    "value": "asdfa",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "112321fd",
                    "value": "112321fd",
                },
            ],
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {
                    "enabled": True,
                    "index": 0,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": True,
                    "index": 1,
                    "indices": [],
                    "name": "asdfa",
                    "value": "asdfa",
                },
                {
                    "enabled": True,
                    "index": 2,
                    "indices": [],
                    "name": "112321fd",
                    "value": "112321fd",
                },
            ],
        )
        prompt._toggle_all(True)
        self.assertEqual(
            prompt.content_control.choices,
            [
                {
                    "enabled": True,
                    "index": 0,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": True,
                    "index": 1,
                    "indices": [],
                    "name": "asdfa",
                    "value": "asdfa",
                },
                {
                    "enabled": True,
                    "index": 2,
                    "indices": [],
                    "name": "112321fd",
                    "value": "112321fd",
                },
            ],
        )
        prompt._toggle_all()
        self.assertEqual(
            prompt.content_control.choices,
            [
                {
                    "enabled": False,
                    "index": 0,
                    "indices": [],
                    "name": "haha",
                    "value": "haha",
                },
                {
                    "enabled": False,
                    "index": 1,
                    "indices": [],
                    "name": "asdfa",
                    "value": "asdfa",
                },
                {
                    "enabled": False,
                    "index": 2,
                    "indices": [],
                    "name": "112321fd",
                    "value": "112321fd",
                },
            ],
        )

    def test_wait_time(self):
        self.prompt.content_control.choices = []
        self.assertEqual(self.prompt._calculate_wait_time(), 0.0)
        self.prompt.content_control.choices = [{} for _ in range(9)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.0)
        self.prompt.content_control.choices = [{} for _ in range(50)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.05)
        self.prompt.content_control.choices = [{} for _ in range(100)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.1)
        self.prompt.content_control.choices = [{} for _ in range(1000)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.2)
        self.prompt.content_control.choices = [{} for _ in range(10000)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.3)
        self.prompt.content_control.choices = [{} for _ in range(100000)]
        self.assertEqual(self.prompt._calculate_wait_time(), 0.6)
        self.prompt.content_control.choices = [{} for _ in range(1000000)]
        self.assertEqual(self.prompt._calculate_wait_time(), 1.2)

    @patch.object(InquirerPyUIControl, "retrieve_choices", new_callable=PropertyMock)
    @patch.object(BaseComplexPrompt, "loading", new_callable=PropertyMock)
    @patch("asyncio.create_task")
    def test_after_render(self, mocked, mocked_loading, mocked_choices):
        class Task(NamedTuple):
            add_done_callback: Callable

        mocked.return_value = Task(add_done_callback=lambda _: True)
        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        self.assertEqual(prompt._rendered, False)
        prompt._after_render("")

        mocked.assert_called()
        mocked_loading.assert_called_once()
        mocked_choices.assert_called_once()
        self.assertEqual(prompt._rendered, True)

    def test_retrieve_choices(self):
        async def retrieve_choices(content_control) -> None:
            await content_control.retrieve_choices()

        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        self.assertEqual(prompt.content_control.choices, [])
        asyncio.run(retrieve_choices(prompt.content_control))
        self.assertEqual(
            prompt.content_control.choices,
            [
                {"enabled": False, "index": 0, "indices": [], "name": "1", "value": 1},
                {"enabled": False, "index": 1, "indices": [], "name": "2", "value": 2},
                {"enabled": False, "index": 2, "indices": [], "name": "3", "value": 3},
            ],
        )

    def test_prompt_filter(self):
        prompt = FuzzyPrompt(
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

    def test_prompt_validator_index(self):
        class Hello(NamedTuple):
            cancelled: Callable
            result: Callable

        class App(NamedTuple):
            exit: Callable

        class Event(NamedTuple):
            app: NamedTuple

        hello = Hello(cancelled=lambda: False, result=lambda: [])
        self.prompt._filter_callback(hello)

        event = Event(App(exit=lambda result: True))
        self.prompt._handle_enter(event)

    def test_loading(self):
        async def run_spinner(prompt) -> None:
            prompt.loading = True
            self.assertTrue(prompt.loading)
            prompt.loading = False

        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        asyncio.run(run_spinner(prompt))
        self.assertFalse(prompt.loading)
