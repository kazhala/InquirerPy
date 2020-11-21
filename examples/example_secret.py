from InquirerPy.resolver import prompt
from InquirerPy.validator import EmptyInputValidator

questions = [
    {"type": "secret", "question": "Enter your password", "default": "1"},
    {
        "type": "secret",
        "question": "Enter secret",
        "name": "secret_key",
        "symbol": "*",
        "validator": EmptyInputValidator(),
    },
]
result = prompt(questions, editing_mode="vim")

print(result)
