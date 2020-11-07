import io
import sys
import unittest
from unittest.mock import patch

from prompt_toolkit.input.defaults import create_pipe_input
from prompt_toolkit.keys import Keys
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.confirm import Confirm


class TestConfirmPrompt(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_confirm_prompt(self):
        self.inp.send_text("\n")
        confirm_prompt = Confirm(
            message="hello",
            style={"symbol": "bold"},
            default_true=False,
            symbol="x",
            output=DummyOutput(),
            input=self.inp,
        )
        result = confirm_prompt.session.prompt()
        self.assertEqual(result, "")
