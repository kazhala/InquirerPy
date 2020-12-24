from contextlib import ExitStack
from pathlib import Path
import urllib.request

from InquirerPy.resolver import prompt


def get_choices():
    p = Path(__file__).resolve().parent.joinpath("sample.txt")
    choices = []

    with ExitStack() as stack:
        if not p.exists():
            print("hello")
            file = stack.enter_context(p.open("w+"))
            sample = stack.enter_context(
                urllib.request.urlopen(
                    "https://kazhala-public-shit.s3-ap-southeast-2.amazonaws.com/sample.txt"
                )
            )
            file.write(sample.read().decode())
            file.seek(0, 0)
        else:
            file = stack.enter_context(p.open("r"))
        for line in file.readlines():
            choices.append(line[:-1])
    return choices


questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": get_choices,
        "border": True,
        "multiselect": True,
        "max_height": "100%",
        "validate": lambda x: len(x) > 1,
    },
    {
        "type": "fuzzy",
        "message": "Select one",
        "choices": ["hello", "weather", "what", "whoa", "hey", "yo"],
        "default": "he",
    },
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
