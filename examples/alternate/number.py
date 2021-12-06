from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator


def main() -> None:
    result = inquirer.number(
        message="Enter a number:",
        min_allowed=-2,
        max_allowed=10,
        validate=EmptyInputValidator(),
        vi_mode=True,
    ).execute()


if __name__ == "__main__":
    main()
