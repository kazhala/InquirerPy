from InquirerPy import inquirer
from InquirerPy.base.control import Choice
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
    regions = inquirer.checkbox(
        message="Select regions:",
        choices=question1_choice,
        cycle=False,
        transformer=lambda result: "%s region%s selected"
        % (len(result), "s" if len(result) > 1 else ""),
    ).execute()
    fruits = inquirer.checkbox(
        message="Pick your favourites:",
        choices=question2_choice,
        validate=lambda result: len(result) >= 1,
        invalid_message="should be at least 1 selection",
        instruction="(select at least 1)",
    ).execute()


if __name__ == "__main__":
    main()
