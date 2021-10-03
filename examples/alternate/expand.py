from InquirerPy import inquirer
from InquirerPy.separator import Separator

question1_choice = [
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
    fruit = inquirer.expand(
        message="Pick your favourite:", choices=question1_choice, default="o"
    ).execute()
    method = inquirer.expand(
        message="Select your preferred method:", choices=question2_choice
    ).execute()


if __name__ == "__main__":
    main()
