from InquirerPy import prompt
from InquirerPy.validator import PasswordValidator

original_password = "InquirerPy45@"


def main():
    questions = [
        {
            "type": "password",
            "message": "Old password:",
            "transformer": lambda _: "[hidden]",
            "validate": lambda text: text == original_password,
            "invalid_message": "Wrong password",
            "long_instruction": "Original password: InquirerPy45@",
        },
        {
            "type": "password",
            "message": "New password:",
            "name": "new_password",
            "validate": PasswordValidator(
                length=8, cap=True, special=True, number=True
            ),
            "transformer": lambda _: "[hidden]",
            "long_instruction": "Password require length of 8, 1 cap char, 1 special char and 1 number char.",
        },
        {"type": "confirm", "message": "Confirm?", "default": True},
    ]
    result = prompt(questions)


if __name__ == "__main__":
    main()
