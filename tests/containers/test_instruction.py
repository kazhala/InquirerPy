import unittest

from InquirerPy.containers.instruction import InstructionWindow


class TestInstructionWindow(unittest.TestCase):
    def test_get_message(self):
        window = InstructionWindow(message="hello", filter=True, wrap_lines=True)
        self.assertEqual(window._get_message(), [("class:instruction", "hello")])
