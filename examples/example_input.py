from InquirerPy.resolver import prompt

questions = [
    {"type": "input", "question": "Enter your name"},
    {
        "type": "input",
        "question": "What do you want",
        "completer": {"hello": None, "what": None, "hey": None},
    },
    {"type": "input", "question": "What do you want", "multiline": True},
]

result = prompt(questions, editing_mode="vim")
print(result)
