from InquirerPy.resolver import prompt

questions = [
    {
        "type": "secret",
        "question": "Enter your password",
    },
    {
        "type": "secret",
        "question": "Enter secret",
        "name": "secret_key",
        "symbol": "*",
        "validator": lambda x: len(x) > 0,
    },
]
result = prompt(questions, editing_mode="vim")

print(result)
