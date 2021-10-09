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
        long_instruction="Original password: InquirerPy45@",
    ).execute()
    new_password = inquirer.secret(
        message="New password:",
        validate=PasswordValidator(length=8, cap=True, special=True, number=True),
        transformer=lambda _: "[hidden]",
        long_instruction="Password require length of 8, 1 cap char, 1 special char and 1 number char.",
    ).execute()
    confirm = inquirer.confirm(message="Confirm?", default=True).execute()


if __name__ == "__main__":
    main()
