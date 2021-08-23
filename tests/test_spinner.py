import asyncio
import unittest

from prompt_toolkit.filters.base import Condition, Filter
from prompt_toolkit.layout.containers import ConditionalContainer

from InquirerPy.containers.spinner import SPINNERS, SpinnerWindow


class TestSpinner(unittest.TestCase):
    def setUp(self) -> None:
        self.spinner = SpinnerWindow(Condition(lambda: True), redraw=lambda: None)

    def test_init(self) -> None:
        self.assertIsInstance(self.spinner, ConditionalContainer)
        self.assertIsInstance(self.spinner._loading, Filter)
        self.assertEqual(self.spinner._pattern, SPINNERS.line)
        self.assertEqual(self.spinner._text, "Loading ...")

        spinner = SpinnerWindow(
            Condition(lambda: True),
            redraw=lambda: None,
            delay=0.2,
            pattern=SPINNERS.dots,
            text="Hello",
        )
        self.assertEqual(spinner._pattern, SPINNERS.dots)
        self.assertEqual(spinner._text, "Hello")
        self.assertEqual(spinner._delay, 0.2)

    def test_get_text(self):
        self.assertEqual(
            self.spinner._get_text(),
            [
                ("class:spinner_pattern", SPINNERS.line[0]),
                ("", " "),
                ("class:spinner_text", "Loading ..."),
            ],
        )

    def test_start(self):
        flag = {"loading": True, "counter": 0}

        async def run_start(spinner) -> None:
            asyncio.create_task(spinner.start())
            asyncio.create_task(spinner.start())
            await asyncio.sleep(0.4)
            flag["loading"] = False

        def count():
            flag["counter"] += 1

        spinner = SpinnerWindow(Condition(lambda: flag["loading"]), redraw=count)
        asyncio.run(run_start(spinner))
        self.assertNotEqual(flag["counter"], 0)
