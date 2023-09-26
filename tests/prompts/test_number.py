import unittest
from decimal import Decimal
from unittest.mock import ANY, call, patch

from prompt_toolkit.keys import Keys

from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.number import NumberPrompt


class TestNumberPrompt(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt = NumberPrompt(
            message="Hello",
            default=1,
            max_allowed=10,
            min_allowed=-2,
            replace_mode=True,
        )
        self.float_prompt = NumberPrompt(
            message="Hello",
            float_allowed=True,
            default=1,
            max_allowed=10,
            min_allowed=-2,
            replace_mode=True,
        )
        self.prompt._on_rendered(None)
        self.float_prompt._on_rendered(None)

    def test_constructor(self) -> None:
        self.assertFalse(self.prompt._float)
        self.assertEqual(self.prompt._default, 1)
        self.assertFalse(self.prompt._is_float())
        self.assertEqual(self.prompt.focus, self.prompt._whole_window)

        prompt = NumberPrompt(message="", default=lambda _: 1)
        self.assertEqual(prompt._default, 1)

        try:
            NumberPrompt(message="", default="asdfasd")
            NumberPrompt(message="", default="asdfas", float_allowed=True)
        except InvalidArgument:
            pass
        else:
            self.fail("InvalidArgument should be raised")

    def test_float_constructor(self) -> None:
        self.assertTrue(self.float_prompt._float)
        self.assertEqual(self.float_prompt._default, 1.0)
        self.assertTrue(self.float_prompt._is_float())

    @patch("InquirerPy.prompts.number.NumberPrompt.register_kb")
    def test_kb_registered(self, mocked_kb) -> None:
        prompt = NumberPrompt(message="")
        mocked_kb.assert_has_calls([call(Keys.Any)])

        prompt._after_render(None)
        mocked_kb.assert_has_calls([call("down", filter=ANY)])
        mocked_kb.assert_has_calls([call("up", filter=ANY)])
        mocked_kb.assert_has_calls([call("left", filter=ANY)])
        mocked_kb.assert_has_calls([call(Keys.Tab, filter=ANY)])
        for i in range(10):
            mocked_kb.assert_has_calls([call(str(i), filter=ANY)])

    def test_on_rendered(self) -> None:
        self.prompt._on_rendered(None)
        self.assertEqual(self.prompt._whole_buffer.text, "1")
        self.assertEqual(self.prompt._integral_buffer.text, "0")
        self.assertFalse(self.prompt._whole_replace)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

        self.float_prompt._default = 1.1
        self.float_prompt._on_rendered(None)
        self.assertEqual(self.float_prompt._whole_buffer.text, "1")
        self.assertEqual(self.float_prompt._integral_buffer.text, "1")
        self.assertTrue(self.prompt._integral_buffer)
        self.assertEqual(self.prompt._integral_buffer.cursor_position, 0)

    def test_on_rendered_sn(self) -> None:
        prompt = NumberPrompt(
            message="", default=0.000000123, float_allowed=True, replace_mode=True
        )
        prompt._on_rendered(None)
        self.assertTrue(prompt._whole_replace)
        self.assertFalse(prompt._integral_replace)
        self.assertEqual(prompt._whole_buffer.text, "0")
        self.assertEqual(prompt._integral_buffer.text, "000000123")

        prompt = NumberPrompt(
            message="", default=0.00000000099912312, float_allowed=True
        )
        prompt._on_rendered(None)
        self.assertEqual(prompt._integral_buffer.text, "00000000099912312")

    def test_handle_down(self) -> None:
        self.prompt._on_rendered(None)
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "0")
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-1")
        self.prompt._handle_down(None)
        self.prompt._handle_down(None)
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-2")

        self.prompt._whole_buffer.text = ""
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "0")

    def test_handle_down_float(self) -> None:
        self.float_prompt._default = 0.3
        self.float_prompt._on_rendered(None)
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_down(None)
        self.assertEqual(self.float_prompt._integral_buffer.text, "2")
        self.float_prompt._handle_down(None)
        self.float_prompt._handle_down(None)
        self.float_prompt._handle_down(None)
        self.float_prompt._handle_down(None)
        self.assertEqual(self.float_prompt._integral_buffer.text, "0")

    def test_handle_up(self) -> None:
        self.prompt._on_rendered(None)
        self.prompt._handle_up(None)
        self.assertEqual(self.prompt._whole_buffer.text, "2")
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.assertEqual(self.prompt._whole_buffer.text, "5")
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.prompt._handle_up(None)
        self.assertEqual(self.prompt._whole_buffer.text, "10")

        self.prompt._whole_buffer.text = ""
        self.prompt._handle_up(None)
        self.assertEqual(self.prompt._whole_buffer.text, "0")

    def test_handle_up_float(self) -> None:
        self.float_prompt._default = 9.0
        self.float_prompt._on_rendered(None)
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_up(None)
        self.assertEqual(self.float_prompt._integral_buffer.text, "1")
        self.float_prompt._handle_up(None)
        self.assertEqual(self.float_prompt._integral_buffer.text, "2")
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_up(None)
        self.assertEqual(self.float_prompt._integral_buffer.text, "2")

    def test_handle_left(self) -> None:
        self.prompt._on_rendered(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_left(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)
        self.prompt._handle_left(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)

    def test_handle_left_float(self) -> None:
        self.float_prompt._on_rendered(None)
        self.assertEqual(self.float_prompt._whole_buffer.cursor_position, 1)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.float_prompt._integral_buffer.cursor_position = 1
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_left(None)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._integral_window)
        self.float_prompt._handle_left(None)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._whole_window)
        self.assertEqual(self.float_prompt._whole_buffer.cursor_position, 1)
        self.float_prompt._handle_left(None)
        self.assertEqual(self.float_prompt._whole_buffer.cursor_position, 0)

    def test_handle_right(self) -> None:
        self.prompt._on_rendered(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.assertEqual(self.prompt.focus, self.prompt._whole_window)
        self.prompt._handle_right(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.assertNotEqual(self.prompt.focus, self.prompt._integral_window)

        self.prompt._whole_buffer.cursor_position = 0
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)
        self.prompt._handle_right(None)
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

    def test_handle_right_float(self) -> None:
        self.float_prompt._on_rendered(None)
        self.assertEqual(self.float_prompt._whole_buffer.cursor_position, 1)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._whole_window)
        self.float_prompt._handle_right(None)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._integral_window)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.float_prompt._handle_right(None)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 1)
        self.float_prompt._handle_right(None)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 1)

    def test_handle_enter(self) -> None:
        self.prompt._on_rendered(None)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.prompt._handle_enter(event)
        self.assertTrue(self.prompt.status["answered"])
        self.assertEqual(self.prompt.status["result"], "1")

        self.prompt._whole_buffer.text = ""
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.prompt._handle_enter(event)
        self.assertTrue(self.prompt.status["answered"])
        self.assertEqual(self.prompt.status["result"], "")

    def test_handle_enter_float(self) -> None:
        self.float_prompt._on_rendered(None)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.float_prompt._handle_enter(event)
        self.assertTrue(self.float_prompt.status["answered"])
        self.assertEqual(self.float_prompt.status["result"], "1.0")

        self.float_prompt._integral_buffer.text = ""
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.float_prompt._handle_enter(event)
        self.assertTrue(self.float_prompt.status["answered"])
        self.assertEqual(self.float_prompt.status["result"], "1.0")

        self.float_prompt._integral_buffer.text = ""
        self.float_prompt._whole_buffer.text = ""
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.float_prompt._handle_enter(event)
        self.assertTrue(self.float_prompt.status["answered"])
        self.assertEqual(self.float_prompt.status["result"], "")

    def test_handle_enter_validation(self) -> None:
        prompt = NumberPrompt(message="", validate=lambda x: x == 1)
        prompt._on_rendered(None)
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            prompt._handle_enter(event)
        self.assertFalse(prompt.status["answered"])
        self.assertEqual(prompt.status["result"], None)
        self.assertEqual(
            prompt._get_error_message(), [("class:validation-toolbar", "Invalid input")]
        )

    def test_handle_focus(self) -> None:
        self.assertEqual(self.prompt.focus, self.prompt._whole_window)
        self.prompt._handle_focus(None)
        self.assertEqual(self.prompt.focus, self.prompt._whole_window)

    def test_handle_focus_float(self) -> None:
        self.assertEqual(self.float_prompt.focus, self.float_prompt._whole_window)
        self.float_prompt._handle_focus(None)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._integral_window)
        self.float_prompt._handle_focus(None)
        self.assertEqual(self.float_prompt.focus, self.float_prompt._whole_window)

    def test_handle_input(self) -> None:
        with patch("prompt_toolkit.utils.Event") as mock:
            event = mock.return_value
            self.prompt._whole_buffer.cursor_position = 0
            self.prompt._handle_input(event)

    @patch("InquirerPy.prompts.number.NumberPrompt._on_text_change")
    def test_on_text_change(self, mocked_text) -> None:
        self.prompt._whole_buffer.text = "10"
        mocked_text.assert_called()
        self.assertEqual(self.prompt._whole_width, 3)

        mocked_text.reset_mock()
        self.float_prompt._integral_buffer.text = "10"
        mocked_text.assert_called()
        self.assertEqual(self.float_prompt._integral_width, 3)
        self.float_prompt._integral_buffer.text = "100"
        self.assertEqual(self.float_prompt._integral_width, 4)

    def test_handle_negative_toggle(self) -> None:
        self.assertEqual(self.prompt._whole_buffer.text, "1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 2)
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

        self.prompt._min = -10
        self.prompt._max = 10
        self.prompt._whole_buffer.text = "10"

        self.prompt._whole_buffer.cursor_position = 2
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 3)
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 2)

        self.prompt._whole_buffer.cursor_position = 1
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 2)
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

        self.prompt._whole_buffer.cursor_position = 0
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)

        self.prompt._whole_buffer.text = "-"
        self.prompt._handle_negative_toggle(None)
        self.assertEqual(self.prompt._whole_buffer.text, "0")

    def test_cursor_position(self) -> None:
        self.prompt._handle_negative_toggle(None)
        self.prompt._whole_buffer.cursor_position = 0
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

    def test_value(self) -> None:
        self.prompt._whole_buffer.text = "asdfad"
        self.assertEqual(self.prompt.value, 1)
        self.assertEqual(
            self.prompt._get_error_message(),
            [("class:validation-toolbar", "Remove any non-integer value")],
        )

    def test_fix_sn(self) -> None:
        left, right = self.prompt._fix_sn("0E-7")
        self.assertEqual(left, "0")
        self.assertEqual(right, "0000000")

        left, right = self.prompt._fix_sn("1.2E-7")
        self.assertEqual(left, "0")
        self.assertEqual(right, "00000012")

        left, right = self.prompt._fix_sn("9.88E-11")
        self.assertEqual(left, "0")
        self.assertEqual(right, "0000000000988")

    def test_handle_number(self) -> None:
        self.prompt._whole_buffer.text = "0"
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

        self.prompt._whole_buffer.text = ""
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "0")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)

        self.prompt._whole_buffer.text = "9"
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 2)
        self.prompt._handle_number(increment=False)
        self.assertEqual(self.prompt._whole_buffer.text, "9")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._whole_buffer.cursor_position = 0
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "10")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_number(increment=False)
        self.assertEqual(self.prompt._whole_buffer.text, "9")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)

        self.prompt._whole_buffer.text = "0"
        self.prompt._whole_buffer.cursor_position = 0
        self.prompt._handle_number(increment=False)
        self.assertEqual(self.prompt._whole_buffer.text, "-1")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 1)
        self.prompt._handle_number(increment=True)
        self.assertEqual(self.prompt._whole_buffer.text, "0")
        self.assertEqual(self.prompt._whole_buffer.cursor_position, 0)

    def test_handle_number_float(self) -> None:
        self.assertEqual(self.float_prompt._integral_buffer.text, "0")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.assertTrue(self.float_prompt._integral_replace)
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_number(increment=True)
        self.assertEqual(self.float_prompt._integral_buffer.text, "1")
        # increased due to buffer starts as replace mode
        self.assertFalse(self.float_prompt._integral_replace)
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 1)

        self.float_prompt._integral_buffer.cursor_position = 0
        self.float_prompt._integral_buffer.text = "001"
        self.float_prompt._handle_number(increment=True)
        self.assertEqual(self.float_prompt._integral_buffer.text, "002")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.float_prompt._handle_number(increment=True)
        self.assertEqual(self.float_prompt._integral_buffer.text, "003")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.float_prompt._handle_number(increment=False)
        self.assertEqual(self.float_prompt._integral_buffer.text, "002")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)
        self.float_prompt._integral_buffer.text = "009"
        self.float_prompt._handle_number(increment=True)
        self.assertEqual(self.float_prompt._integral_buffer.text, "0010")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 1)
        self.float_prompt._handle_number(increment=False)
        self.assertEqual(self.float_prompt._integral_buffer.text, "009")
        self.assertEqual(self.float_prompt._integral_buffer.cursor_position, 0)

    def test_handle_dot(self) -> None:
        self.assertEqual(self.prompt.focus_buffer, self.prompt._whole_buffer)
        self.prompt._handle_dot(None)
        self.assertEqual(self.prompt.focus_buffer, self.prompt._whole_buffer)

        self.assertEqual(
            self.float_prompt.focus_buffer, self.float_prompt._whole_buffer
        )
        self.float_prompt._handle_dot(None)
        self.assertEqual(
            self.float_prompt.focus_buffer, self.float_prompt._integral_buffer
        )
        self.float_prompt._handle_dot(None)
        self.assertEqual(
            self.float_prompt.focus_buffer, self.float_prompt._integral_buffer
        )

    def test_sn(self) -> None:
        self.float_prompt.value = Decimal("0.00000000099912312")
        self.assertEqual(self.float_prompt._integral_buffer.text, "00000000099912312")

        self.float_prompt.value = Decimal("1.1")
        self.assertEqual(self.float_prompt._integral_buffer.text, "1")

    def test_replace_mode(self) -> None:
        self.assertFalse(self.prompt._whole_replace)
        self.assertTrue(self.float_prompt._integral_replace)
        self.float_prompt._handle_focus(None)
        self.float_prompt._handle_left(None)
        self.assertFalse(self.float_prompt._integral_replace)

        prompt = NumberPrompt(message="", float_allowed=True, replace_mode=True)
        prompt._on_rendered(None)
        self.assertTrue(prompt._whole_replace)
        self.assertTrue(prompt._integral_replace)
        prompt._handle_up(None)
        self.assertFalse(prompt._whole_replace)
        prompt._handle_dot(None)
        prompt._handle_right(None)
        self.assertFalse(prompt._integral_replace)

    def test_replace_mode_no(self) -> None:
        prompt = NumberPrompt(message="", replace_mode=False)
        prompt._on_rendered(None)
        self.assertFalse(prompt._whole_replace)
        self.assertFalse(prompt._integral_replace)

    def test_empty_default(self) -> None:
        prompt = NumberPrompt(message="", default=None)
        prompt._on_rendered(None)
        self.assertEqual(prompt._whole_buffer.text, "")
        self.assertEqual(prompt._integral_buffer.text, "")

        prompt = NumberPrompt(message="", default=None, float_allowed=True)
        prompt._on_rendered(None)
        self.assertEqual(prompt._whole_buffer.text, "")
        self.assertEqual(prompt._integral_buffer.text, "")

    def test_empty_buffer(self) -> None:
        prompt = NumberPrompt(message="", default=None, float_allowed=True)
        prompt._on_rendered(None)
        self.assertEqual(prompt._whole_buffer.text, "")
        self.assertEqual(prompt._integral_buffer.text, "")
        prompt._whole_buffer.text = "1"
        self.assertEqual(prompt._whole_buffer.text, "1")
        self.assertEqual(prompt._integral_buffer.text, "")
        self.assertEqual(str(prompt.value), "1.0")

        prompt._whole_buffer.text = ""
        prompt._integral_buffer.text = "1"
        self.assertEqual(prompt._whole_buffer.text, "")
        self.assertEqual(prompt._integral_buffer.text, "1")
        self.assertEqual(str(prompt.value), "0.1")
