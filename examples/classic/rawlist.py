from InquirerPy import prompt
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def main():
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
                Choice(name="Delivery", value="dl"),
                Choice(name="Pick Up", value="pk"),
                Separator(line=15 * "*"),
                Choice(name="Car Park", value="cp"),
                Choice(name="Third Party", value="tp"),
            ],
            "message": "Select your preferred method:",
        },
    ]

    result = prompt(questions)


if __name__ == "__main__":
    main()
