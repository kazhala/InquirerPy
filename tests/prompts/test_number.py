import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.keys import Keys

from InquirerPy.prompts.number import NumberPrompt


class TestNumberPrompt(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt = NumberPrompt(message="Hello", default=1)
        self.float_prompt = NumberPrompt(message="Hello", float_allowed=True, default=1)

    def test_contructor(self) -> None:
        self.assertFalse(self.prompt._float)
        self.assertEqual(self.prompt._default, 1)
        self.assertFalse(self.prompt._is_float())
        self.assertEqual(self.prompt.focus, self.prompt._whole_window)

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

        self.float_prompt._default = 1.1
        self.float_prompt._on_rendered(None)
        self.assertEqual(self.float_prompt._whole_buffer.text, "1")
        self.assertEqual(self.float_prompt._integral_buffer.text, "1")

    def test_handle_down(self) -> None:
        self.prompt._on_rendered(None)
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "0")
        self.prompt._handle_down(None)
        self.assertEqual(self.prompt._whole_buffer.text, "-1")
        self.assertEqual(self.prompt._integral_buffer.text, "0")

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
