from InquirerPy.resolver import prompt
from InquirerPy.validator import EmptyInputValidator, PasswordValidator

questions = [
    {"type": "secret", "message": "Enter your password", "default": "1"},
    {
        "type": "secret",
        "message": "Enter secret",
        "name": "secret_key",
        "symbol": "*",
        "validator": EmptyInputValidator(),
    },
    {
        "type": "secret",
        "message": "New password",
        "name": "password",
        "validator": PasswordValidator(length=8, cap=True, special=True, number=True),
    },
]
result = prompt(questions, editing_mode="vim")

print(result)
