from InquirerPy import prompt
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def main():
    questions = [
        {
            "type": "list",
            "message": "Select an action:",
            "choices": ["Upload", "Download", Choice(value=None, name="Exit")],
            "default": None,
        },
        {
            "type": "list",
            "message": "Select regions:",
            "choices": [
                Choice("ap-southeast-2", name="Sydney"),
                Choice("ap-southeast-1", name="Singapore"),
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            "multiselect": True,
            "transformer": lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
            "when": lambda result: result[0] is not None,
        },
    ]

    result = prompt(questions=questions)


if __name__ == "__main__":
    main()
