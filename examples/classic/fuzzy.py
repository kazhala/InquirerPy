import urllib.request
from contextlib import ExitStack
from pathlib import Path

from InquirerPy import prompt


def get_choices(_):
    p = Path(__file__).resolve().parent.joinpath("sample.txt")
    choices = []
    result = []

    with ExitStack() as stack:
        if not p.exists():
            file = stack.enter_context(p.open("w+"))
            sample = stack.enter_context(
                urllib.request.urlopen(
                    "https://assets.kazhala.me/InquirerPy/sample.txt"
                )
            )
            file.write(sample.read().decode())
            file.seek(0, 0)
        else:
            file = stack.enter_context(p.open("r"))
        for line in file.readlines():
            choices.append(line[:-1])
        for choice in choices:
            if not choice:
                continue
            result.append(choice)
    return result


def main():
    questions = [
        {
            "type": "fuzzy",
            "message": "Select actions:",
            "choices": ["hello", "weather", "what", "whoa", "hey", "yo"],
            "default": "he",
            "max_height": "70%",
        },
        {
            "type": "fuzzy",
            "message": "Select preferred words:",
            "choices": get_choices,
            "multiselect": True,
            "validate": lambda result: len(result) > 1,
            "invalid_message": "minimum 2 selection",
            "max_height": "70%",
        },
    ]

    result = prompt(questions=questions)


if __name__ == "__main__":
    main()
