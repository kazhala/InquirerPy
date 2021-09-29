from InquirerPy import inquirer
from InquirerPy.separator import Separator


def main():
    action = inquirer.select(
        message="Select an action:",
        choices=["Upload", "Download", {"name": "Exit", "value": None}],
        default=None,
    ).execute()
    if action:
        region = inquirer.select(
            message="Select regions:",
            choices=[
                {"name": "Sydney", "value": "ap-southeast-2"},
                {"name": "Singapore", "value": "ap-southeast-1"},
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            multiselect=True,
            transformer=lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
        ).execute()


if __name__ == "__main__":
    main()
