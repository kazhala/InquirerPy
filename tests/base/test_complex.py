import asyncio
import unittest
from typing import Callable, NamedTuple
from unittest.mock import ANY, PropertyMock, call, patch

from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

from InquirerPy.base.complex import BaseComplexPrompt
from InquirerPy.base.control import InquirerPyUIControl
from InquirerPy.base.list import BaseListPrompt
from InquirerPy.containers.spinner import SPINNERS
from InquirerPy.prompts.fuzzy import FuzzyPrompt


class TestBaseComplex(unittest.TestCase):
    @patch("InquirerPy.base.complex.SpinnerWindow")
    def test_constructor(self, mocked_spinner) -> None:
        mocked_spinner.return_value = Window(
            content=FormattedTextControl(text=[("", "")])
        )
        fuzzy_prompt = FuzzyPrompt(message="hello", choices=["1", "2", "3"])
        mocked_spinner.assert_called_with(
            loading=ANY,
            redraw=fuzzy_prompt._redraw,
            pattern=None,
            text="hello",
            delay=0.1,
        )

        fuzzy_prompt = FuzzyPrompt(
            message="hello",
            choices=["1", "2", "3"],
            spinner_text="Loading",
            spinner_pattern=SPINNERS.line,
        )
        mocked_spinner.assert_called_with(
            loading=ANY,
            redraw=fuzzy_prompt._redraw,
            pattern=SPINNERS.line,
            text="Loading",
            delay=0.1,
        )

    def test_register_kb(self) -> None:
        fuzzy_prompt = FuzzyPrompt(message="hello", choices=["1", "2", "3"])

        @fuzzy_prompt._register_kb("c-q")
        def hello(_):
            pass

        self.assertFalse(fuzzy_prompt._invalid)
        fuzzy_prompt._invalid = True
        hello("")  # type: ignore
        self.assertFalse(fuzzy_prompt._invalid)

    @patch.object(BaseComplexPrompt, "_register_kb")
    @patch.object(InquirerPyUIControl, "retrieve_choices", new_callable=PropertyMock)
    @patch.object(BaseListPrompt, "loading", new_callable=PropertyMock)
    @patch("asyncio.create_task")
    def test_after_render(self, mocked, mocked_loading, mocked_choices, mocked_kb):
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
        mocked_kb.assert_has_calls(
            [
                call("down", filter=ANY),
            ]
        )
        mocked_kb.assert_has_calls(
            [
                call("c-n", filter=ANY),
            ]
        )

    def test_prompt_message(self):
        prompt = FuzzyPrompt(message="Select one of them", choices=lambda _: [1, 2, 3])

        self.assertEqual(
            prompt._get_prompt_message(),
            [
                ("class:questionmark", "?"),
                ("class:question", " Select one of them"),
                ("class:instruction", " "),
            ],
        )
        prompt.status = {"answered": True, "result": ["hello"]}
        self.assertEqual(
            prompt._get_prompt_message(),
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

    def test_content_control(self):
        prompt = FuzzyPrompt(message="Select one of them", choices=lambda _: [1, 2, 3])
        prompt.content_control = None  # type: ignore
        try:
            prompt.content_control
        except NotImplementedError:
            pass
        else:
            self.fail("NotImplemented not raised.")

    def test_result_name_simple(self):
        prompt = FuzzyPrompt(message="Select one of them", choices=[1, 2, 3])
        self.assertEqual(prompt.result_name, "1")
        prompt.content_control.selected_choice_index = 1
        self.assertEqual(prompt.result_name, "2")

        prompt.content_control.selected_choice_index = 4
        self.assertEqual(prompt.result_name, "")

    def test_result_name_multi(self):
        prompt = FuzzyPrompt(
            message="Select one of them", choices=[1, 2, 3], multiselect=True
        )
        self.assertEqual(prompt.result_name, [])
        prompt.content_control.choices[0]["enabled"] = True
        prompt.content_control.choices[2]["enabled"] = True
        self.assertEqual(prompt.result_name, ["1", "3"])

    def test_result_value_simple(self):
        prompt = FuzzyPrompt(message="Select one of them", choices=[1, 2, 3])

        self.assertEqual(prompt.result_value, 1)
        prompt.content_control.selected_choice_index = 1
        self.assertEqual(prompt.result_value, 2)

        prompt.content_control.selected_choice_index = 4
        self.assertEqual(prompt.result_value, "")

    def test_result_value_multi(self):
        prompt = FuzzyPrompt(
            message="Select one of them", choices=[1, 2, 3], multiselect=True
        )
        self.assertEqual(prompt.result_value, [])
        prompt.content_control.choices[0]["enabled"] = True
        prompt.content_control.choices[2]["enabled"] = True
        self.assertEqual(prompt.result_value, [1, 3])

    def test_application(self):
        prompt = FuzzyPrompt(message="Select one of them", choices=lambda _: [1, 2, 3])
        prompt._application = None  # type: ignore
        try:
            prompt.application
        except NotImplementedError:
            pass
        else:
            self.fail("NotImplemented not raised.")

    def test_handle_down(self):
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)

    def test_handle_down_no_cycle(self):
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
            cycle=False,
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_down()
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 4)

    def test_handle_up(self):
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_up()
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up()
        prompt._handle_up()
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 4)

    def test_handle_up_no_cycle(self):
        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
            cycle=False,
        )
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up()
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down()
        prompt._handle_down()
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up()
        prompt._handle_up()
        prompt._handle_up()
        prompt._handle_up()
        self.assertEqual(prompt.content_control.selected_choice_index, 0)

        prompt = FuzzyPrompt(
            message="Select one of them",
            choices=[
                "haah",
                "haha",
                "what",
                "waht",
                {"name": "weaht", "value": "weaht", "enabled": True},
            ],
            cycle=False,
        )

    @patch("InquirerPy.utils.shutil.get_terminal_size")
    def test_wrap_lines_offset(self, mocked_term):
        mocked_term.return_value = (24, 80)
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
        self.assertEqual(
            prompt.wrap_lines_offset,
            (len(qmark) + 1 + len(message) + 1 + len(instruction) + 1) // 24,
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
        self.assertEqual(
            prompt.wrap_lines_offset,
            (len(qmark) + 1 + len(message) + 1 + len(instruction) + 1) // 24,
        )
        prompt._wrap_lines = False
        self.assertEqual(prompt.wrap_lines_offset, 0)

    def test_loading(self):
        async def run_spinner(prompt) -> None:
            prompt.loading = True
            self.assertTrue(prompt.loading)
            prompt.loading = False

        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        asyncio.run(run_spinner(prompt))
        self.assertFalse(prompt.loading)
