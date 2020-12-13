from InquirerPy.resolver import prompt
from InquirerPy.validator import EmptyInputValidator, PasswordValidator

questions = [
    {
        "type": "secret",
        "message": "Enter your password",
        "default": "1",
        "transformer": lambda x: x * 2,
    },
    {
        "type": "secret",
        "message": "Enter secret",
        "name": "secret_key",
        "qmark": "*",
        "validate": EmptyInputValidator(),
    },
    {
        "type": "secret",
        "message": "New password",
        "name": "password",
        "validate": PasswordValidator(length=8, cap=True, special=True, number=True),
    },
]
result = prompt(questions, editing_mode="vim")

print(result)
