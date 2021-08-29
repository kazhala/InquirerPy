import unittest

from InquirerPy.containers.tips import TipsWindow


class TestTipsWindow(unittest.TestCase):
    def test_get_message(self):
        window = TipsWindow(message="hello", filter=True, wrap_lines=True)
        self.assertEqual(window._get_message(), [("class:instruction", "hello")])
