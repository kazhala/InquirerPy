from InquirerPy import inquirer
from InquirerPy.prompts.expand import ExpandChoice
from InquirerPy.separator import Separator

question1_choice = [
    ExpandChoice(key="a", name="Apple", value="Apple"),
    ExpandChoice(key="c", name="Cherry", value="Cherry"),
    ExpandChoice(key="o", name="Orange", value="Orange"),
    ExpandChoice(key="p", name="Peach", value="Peach"),
    ExpandChoice(key="m", name="Melon", value="Melon"),
    ExpandChoice(key="s", name="Strawberry", value="Strawberry"),
    ExpandChoice(key="g", name="Grapes", value="Grapes"),
]


def question2_choice(_):
    return [
        ExpandChoice(key="d", name="Delivery", value="dl"),
        ExpandChoice(key="p", name="Pick Up", value="pk"),
        Separator(line=15 * "*"),
        ExpandChoice(key="c", name="Car Park", value="cp"),
        ExpandChoice(key="t", name="Third Party", value="tp"),
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
