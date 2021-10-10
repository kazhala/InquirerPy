import asyncio
import unittest
from typing import Callable, NamedTuple
from unittest.mock import ANY, PropertyMock, call, patch

from prompt_toolkit.application.application import Application
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base.complex import BaseComplexPrompt
from InquirerPy.base.control import InquirerPyUIListControl
from InquirerPy.base.list import BaseListPrompt
from InquirerPy.containers.spinner import SPINNERS
from InquirerPy.enum import INQUIRERPY_KEYBOARD_INTERRUPT
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

        @fuzzy_prompt.register_kb("c-q")
        def hello(_):
            pass

        self.assertFalse(fuzzy_prompt._invalid)
        fuzzy_prompt._invalid = True
        hello("")  # type: ignore
        self.assertFalse(fuzzy_prompt._invalid)

    @patch.object(BaseComplexPrompt, "register_kb")
    @patch.object(
        InquirerPyUIListControl, "retrieve_choices", new_callable=PropertyMock
    )
    @patch.object(BaseListPrompt, "loading", new_callable=PropertyMock)
    @patch("asyncio.create_task")
    def test_after_render(self, mocked, mocked_loading, mocked_choices, mocked_kb):
        class Task(NamedTuple):
            add_done_callback: Callable

        mocked.return_value = Task(add_done_callback=lambda _: True)
        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        self.assertEqual(prompt._rendered, False)
        prompt._after_render(None)

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
        prompt.status["answered"] = True
        prompt.status["result"] = ["hello"]
        prompt.status["skipped"] = False

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
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down(None)
        prompt._handle_down(None)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down(None)
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
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 1)
        prompt._handle_down(None)
        prompt._handle_down(None)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_down(None)
        prompt._handle_down(None)
        prompt._handle_down(None)
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
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 4)
        prompt._handle_up(None)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up(None)
        prompt._handle_up(None)
        prompt._handle_up(None)
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
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_up(None)
        prompt._handle_up(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 0)
        prompt._handle_down(None)
        prompt._handle_down(None)
        self.assertEqual(prompt.content_control.selected_choice_index, 2)
        prompt._handle_up(None)
        prompt._handle_up(None)
        prompt._handle_up(None)
        prompt._handle_up(None)
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

    @patch("InquirerPy.base.complex.shutil.get_terminal_size")
    @patch("InquirerPy.utils.shutil.get_terminal_size")
    def test_extra_lines_due_to_offset(self, mocked_term, mocked_term2):
        mocked_term.return_value = (24, 80)
        mocked_term2.return_value = (24, 80)
        message = 15 * "i"
        qmark = "[?]"
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
            prompt.extra_line_count,
            (len(qmark) + 1 + len(message) + 1 + len(instruction) + 1 - 1) // 24,
        )

        instruction = 4 * "i"
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
            prompt.extra_line_count,
            (len(qmark) + 1 + len(message) + 1 + len(instruction) + 1 - 1) // 24,
        )

    @patch("InquirerPy.base.complex.shutil.get_terminal_size")
    def test_height_offset(self, mocked_term) -> None:
        mocked_term.return_value = (24, 80)
        message = 15 * "i"
        qmark = "[?]"
        instruction = 4 * "i"
        prompt = FuzzyPrompt(
            message=message, qmark=qmark, instruction=instruction, choices=[1, 2, 3]
        )
        self.assertEqual(prompt.height_offset, 4)
        prompt._wrap_lines = False
        self.assertEqual(prompt.height_offset, 3)

        prompt = FuzzyPrompt(
            message=message,
            qmark=qmark,
            instruction=instruction,
            choices=[1, 2, 3],
            border=True,
        )
        self.assertEqual(prompt.height_offset, 6)

        instruction = 3 * "i"  # width total should be 24 and no extra lines needed
        prompt = FuzzyPrompt(
            message=message, qmark=qmark, instruction=instruction, choices=[1, 2, 3]
        )
        self.assertEqual(prompt.height_offset, 3)

    def test_loading(self):
        async def run_spinner(prompt) -> None:
            prompt.loading = True
            self.assertTrue(prompt.loading)
            prompt.loading = False

        prompt = FuzzyPrompt(message="", choices=lambda _: [1, 2, 3])
        asyncio.run(run_spinner(prompt))
        self.assertFalse(prompt.loading)

    def test_get_error_message(self):
        class SelectionValidator(Validator):
            def validate(self, document) -> None:
                if document.text == 1:
                    raise ValidationError(
                        message="hello", cursor_position=document.cursor_position
                    )

        prompt = FuzzyPrompt(
            message="",
            choices=[1, 2, 3],
            validate=SelectionValidator(),
            invalid_message="minimum 2 selections",
        )
        self.assertEqual(prompt._invalid_message, "minimum 2 selections")
        self.assertFalse(prompt._invalid)
        prompt._handle_enter(None)
        self.assertEqual(prompt._invalid_message, "hello")
        self.assertTrue(prompt._invalid)
        self.assertEqual(
            prompt._get_error_message(), [("class:validation-toolbar", "hello")]
        )

    @patch.object(Application, "exit")
    def test_exception_handler(self, mocked):
        async def test_async():
            prompt = FuzzyPrompt(message="", choices=[1, 2, 3])
            prompt._after_render(None)
            loop = asyncio.get_running_loop()
            self.assertEqual(prompt._status["answered"], False)
            self.assertEqual(prompt._status["result"], None)
            self.assertEqual(prompt._status["skipped"], False)
            self.assertEqual(loop.get_exception_handler(), prompt._exception_handler)
            prompt._exception_handler(None, {"exception": KeyboardInterrupt})
            self.assertEqual(prompt._status["answered"], True)
            self.assertEqual(prompt._status["result"], INQUIRERPY_KEYBOARD_INTERRUPT)
            self.assertEqual(prompt._status["skipped"], True)

        asyncio.run(test_async())
