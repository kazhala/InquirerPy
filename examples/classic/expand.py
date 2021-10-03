from InquirerPy import prompt
from InquirerPy.separator import Separator


def question1_choice(_):
    return [
        {"key": "a", "name": "Apple", "value": "Apple"},
        {"key": "c", "name": "Cherry", "value": "Cherry"},
        {"key": "o", "name": "Orange", "value": "Orange"},
        {"key": "p", "name": "Peach", "value": "Peach"},
        {"key": "m", "name": "Melon", "value": "Melon"},
        {"key": "s", "name": "Strawberry", "value": "Strawberry"},
        {"key": "g", "name": "Grapes", "value": "Grapes"},
    ]


def question2_choice(_):
    return [
        {"key": "d", "name": "Delivery", "value": "dl"},
        {"key": "p", "name": "Pick Up", "value": "pk"},
        Separator(line=15 * "*"),
        {"key": "c", "name": "Car Park", "value": "cp"},
        {"key": "t", "name": "Third Party", "value": "tp"},
    ]


def main():
    questions = [
        {
            "type": "expand",
            "choices": question1_choice,
            "message": "Pick your favourite:",
            "default": "o",
            "cycle": False,
        },
        {
            "type": "expand",
            "choices": question2_choice,
            "message": "Select your preferred method:",
        },
    ]

    result = prompt(questions)


if __name__ == "__main__":
    main()
