from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def main():
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
            Choice(name="Delivery", value="dl"),
            Choice(name="Pick Up", value="pk"),
            Separator(line=15 * "*"),
            Choice(name="Car Park", value="cp"),
            Choice(name="Third Party", value="tp"),
        ],
    ).execute()


if __name__ == "__main__":
    main()
