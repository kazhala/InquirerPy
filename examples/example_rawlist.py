from InquirerPy import inquirer, prompt
from InquirerPy.separator import Separator


def classic():
    questions = [
        {
            "type": "rawlist",
            "choices": [
                "Apple",
                "Orange",
                "Peach",
                "Cherry",
                "Melon",
                "Strawberry",
                "Grapes",
            ],
            "message": "Pick your favourites:",
            "default": 3,
            "multiselect": True,
            "transformer": lambda result: ", ".join(result),
            "validate": lambda result: len(result) > 1,
            "invalid_message": "Minimum 2 selections",
        },
        {
            "type": "rawlist",
            "choices": [
                {"name": "Delivery", "value": "dl"},
                {"name": "Pick Up", "value": "pk"},
                Separator(line=15 * "*"),
                {"name": "Car Park", "value": "cp"},
                {"name": "Third Party", "value": "tp"},
            ],
            "message": "Select your preferred method:",
        },
    ]

    result = prompt(questions)


def alternate():
    fruit = inquirer.rawlist(
        message="Pick your favourites:",
        choices=[
            "Apple",
            "Orange",
            "Peach",
            "Cherry",
            "Melon",
            "Strawberry",
            "Grapes",
        ],
        default=3,
        multiselect=True,
        transformer=lambda result: ", ".join(result),
        validate=lambda result: len(result) > 1,
        invalid_message="Minimum 2 selections",
    ).execute()
    method = inquirer.rawlist(
        message="Select your preferred method:",
        choices=[
            {"name": "Delivery", "value": "dl"},
            {"name": "Pick Up", "value": "pk"},
            Separator(line=15 * "*"),
            {"name": "Car Park", "value": "cp"},
            {"name": "Third Party", "value": "tp"},
        ],
    ).execute()


alternate()
# classic()
