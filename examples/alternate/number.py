from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator


def main() -> None:
    integer_val = inquirer.number(
        message="Enter integer:",
        min_allowed=-2,
        max_allowed=10,
        validate=EmptyInputValidator(),
    ).execute()
    float_val = inquirer.number(
        message="Enter float:",
        float_allowed=True,
        validate=EmptyInputValidator(),
    ).execute()


if __name__ == "__main__":
    main()
