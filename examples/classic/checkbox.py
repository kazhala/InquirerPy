from InquirerPy import prompt
from InquirerPy.base import Choice
from InquirerPy.separator import Separator

question1_choice = [
    Separator(),
    Choice("ap-southeast-2", name="Sydney", enabled=True),
    Choice("ap-southeast-1", name="Singapore", enabled=False),
    Separator(),
    "us-east-1",
    "us-west-1",
    Separator(),
]


def question2_choice(_):
    return [
        "Apple",
        "Cherry",
        "Orange",
        "Peach",
        "Melon",
        "Strawberry",
        "Grapes",
    ]


def main():
    questions = [
        {
            "type": "checkbox",
            "message": "Select regions:",
            "choices": question1_choice,
            "transformer": lambda result: "%s region%s selected"
            % (len(result), "s" if len(result) > 1 else ""),
        },
        {
            "type": "checkbox",
            "message": "Pick your favourites:",
            "choices": question2_choice,
            "validate": lambda result: len(result) >= 1,
            "invalid_message": "should be at least 1 selection",
            "instruction": "(select at least 1)",
        },
    ]

    result = prompt(questions)


if __name__ == "__main__":
    main()
