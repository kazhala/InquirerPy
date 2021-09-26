from InquirerPy import prompt
from InquirerPy.validator import NumberValidator


def main():
    """Classic syntax example."""
    questions = [
        {"type": "input", "message": "Enter your name:"},
        {
            "type": "input",
            "message": "Which company would you like to apply:",
            "completer": {
                "Google": None,
                "Facebook": None,
                "Amazon": None,
                "Netflix": None,
                "Apple": None,
                "Microsoft": None,
            },
            "multicolumn_complete": True,
        },
        {
            "type": "input",
            "message": "What's your salary expectation(k):",
            "transformer": lambda result: "%sk" % result,
            "filter": lambda result: int(result) * 1000,
            "validate": NumberValidator(),
        },
    ]

    result = prompt(questions)


if __name__ == "__main__":
    main()
