from InquirerPy import inquirer
from InquirerPy.validator import PasswordValidator

original_password = "InquirerPy45@"


def main():
    old_password = inquirer.secret(
        message="Old password:",
        transformer=lambda _: "[hidden]",
        validate=lambda text: text == original_password,
        invalid_message="Wrong password",
        instruction="(abc)",
    ).execute()
    new_password = inquirer.secret(
        message="New password:",
        validate=PasswordValidator(length=8, cap=True, special=True, number=True),
        transformer=lambda _: "[hidden]",
    ).execute()
    confirm = inquirer.confirm(message="Confirm?", default=True).execute()


if __name__ == "__main__":
    main()
