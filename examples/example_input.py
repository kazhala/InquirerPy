from InquirerPy.resolver import prompt

questions = [
    {"type": "input", "message": "Enter your name"},
    {
        "type": "input",
        "message": "What do you want",
        "completer": {"hello": None, "what": None, "hey": None},
    },
    {"type": "input", "message": "What do you want", "multiline": True},
]

result = prompt(questions, editing_mode="vim")
print(result)
