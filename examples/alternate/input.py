from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator


def main():
    """Alternate syntax example."""

    name = inquirer.text(message="Enter your name:").execute()
    company = inquirer.text(
        message="Which company would you like to apply:",
        completer={
            "Google": None,
            "Facebook": None,
            "Amazon": None,
            "Netflix": None,
            "Apple": None,
            "Microsoft": None,
        },
        multicolumn_complete=True,
    ).execute()
    salary = inquirer.text(
        message="What's your salary expectation(k):",
        transformer=lambda result: "%sk" % result,
        filter=lambda result: int(result) * 1000,
        validate=NumberValidator(),
    ).execute()


if __name__ == "__main__":
    main()
