from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator


def main():
    action = inquirer.select(
        message="Select an action:",
        choices=[
            "Upload",
            "Download",
            Choice(value=None, name="Exit"),
        ],
        default=None,
    ).execute()
    if action:
        region = inquirer.select(
            message="Select regions:",
            choices=[
                Choice("ap-southeast-2", name="Sydney"),
                Choice("ap-southeast-1", name="Singapore"),
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            multiselect=True,
            transformer=lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
        ).execute()


if __name__ == "__main__":
    main()
