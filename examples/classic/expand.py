from InquirerPy import prompt
from InquirerPy.prompts.expand import ExpandChoice
from InquirerPy.separator import Separator


def question1_choice(_):
    return [
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
