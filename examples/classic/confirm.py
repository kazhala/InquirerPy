from InquirerPy import prompt


def main():
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": True,
        },
        {
            "type": "confirm",
            "message": "Require 1 on 1?",
            "when": lambda result: result["proceed"],
        },
        {
            "type": "confirm",
            "message": "Confirm?",
            "when": lambda result: result.get("1", False),
        },
    ]

    result = prompt(questions)


if __name__ == "__main__":
    main()
