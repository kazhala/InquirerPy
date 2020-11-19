import unittest
from unittest.mock import patch

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.prompts.secret import Secret


class TestSecret(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_prompt_result(self):
        self.inp.send_text("what\n")
        secret_prompt = Secret(
            message="hello",
            style={"answer": ""},
            default="yes",
            symbol="~",
            editing_mode="default",
            input=self.inp,
            output=DummyOutput(),
        )
        result = secret_prompt.execute()
        self.assertEqual(result, "what")
        self.assertEqual(secret_prompt.status, {"answered": True, "result": "what"})

    @patch.object(Buffer, "validate_and_handle")
    def test_prompt_validation(self):
        self.inp.send_text("\n")

    def test_prompt_message(self):
        pass

    def test_callable_called(self):
        pass
