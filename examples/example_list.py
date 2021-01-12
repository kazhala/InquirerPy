from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator


def classic():
    questions = [
        {
            "type": "list",
            "message": "Select an action:",
            "choices": ["Upload", "Download", {"name": "Exit", "value": None}],
            "default": None,
        },
        {
            "type": "list",
            "message": "Select regions:",
            "choices": [
                {"name": "Sydney", "value": "ap-southeast-2"},
                {"name": "Singapore", "value": "ap-southeast-1"},
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            "multiselect": True,
            "transformer": lambda result: "%s region%s selected"
            % (len(result), "s" if len(result) > 1 else ""),
            "when": lambda result: result["0"] is not None,
        },
    ]

    result = prompt(questions=questions)


classic()
