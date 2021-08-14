import re
import unittest

from InquirerPy import inquirer
from InquirerPy.resolver import question_mapping


class TestInquirer(unittest.TestCase):
    def test_pkgs(self) -> None:
        inquirer_lookup = set()
        special_mapping = {"password": "secret", "input": "text", "list": "select"}
        for pkg in dir(inquirer):
            dunder_pattern = re.compile(r"^__.*")
            if not dunder_pattern.match(pkg):
                inquirer_lookup.add(pkg)

        for prompt in question_mapping.keys():
            prompt = special_mapping.get(prompt, prompt)
            if prompt not in inquirer_lookup:
                self.fail()
