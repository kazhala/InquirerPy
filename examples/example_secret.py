from InquirerPy.resolver import prompt
from InquirerPy.validator import EmptyInputValidator, PasswordValidator

questions = [
    {"type": "secret", "question": "Enter your password", "default": "1"},
    {
        "type": "secret",
        "question": "Enter secret",
        "name": "secret_key",
        "symbol": "*",
        "validator": EmptyInputValidator(),
    },
    {
        "type": "secret",
        "question": "New password",
        "name": "password",
        "validator": PasswordValidator(length=8, cap=True, special=True, number=True),
    },
]
result = prompt(questions, editing_mode="vim")

print(result)
