import time
import urllib.request
from contextlib import ExitStack
from pathlib import Path

from InquirerPy import inquirer, prompt
from InquirerPy.containers.spinner import SPINNERS


def get_choices(_):
    p = Path(__file__).resolve().parent.joinpath("sample.txt")
    choices = []
    time.sleep(1)

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
    return choices


def classic():
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


def alternate():
    action = inquirer.fuzzy(
        message="Select actions:",
        choices=["hello", "weather", "what", "whoa", "hey", "yo"],
        default="he",
        max_height="70%",
    ).execute()
    words = inquirer.fuzzy(
        message="Select preferred words:",
        choices=get_choices,
        multiselect=True,
        validate=lambda result: len(result) > 1,
        invalid_message="minimum 2 selections",
        max_height="70%",
        spinner_enable=True,
        spinner_pattern=SPINNERS.line,
        spinner_text="Fetching sample texts ...",
    ).execute()


alternate()
# classic()
