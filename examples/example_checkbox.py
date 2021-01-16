from InquirerPy import inquirer, prompt
from InquirerPy.separator import Separator


def question1_choice(_):
    return [
        {"name": "Sydney", "value": "ap-southeast-2", "enabled": True},
        {"name": "Singapore", "value": "ap-southeast-1", "enabled": False},
        Separator(),
        "us-east-1",
        "us-west-1",
    ]


def question2_choice(_):
    return [
        {"enabled": False, "name": "Apple", "value": "Apple"},
        {"enabled": False, "name": "Cherry", "value": "Cherry"},
        {"enabled": False, "name": "Orange", "value": "Orange"},
        {"enabled": False, "name": "Peach", "value": "Peach"},
        {"enabled": False, "name": "Melon", "value": "Melon"},
        {"enabled": False, "name": "Strawberry", "value": "Strawberry"},
        {"enabled": False, "name": "Grapes", "value": "Grapes"},
    ]


def classic():
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

    result = prompt(questions, vi_mode=True)


def alternate():
    regions = inquirer.checkbox(
        message="Select regions:",
        choices=question1_choice,
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


alternate()
# classic()
