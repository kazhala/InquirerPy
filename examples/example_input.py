from InquirerPy.resolver import prompt

questions = [
    {"type": "input", "message": "Enter your name"},
    {
        "type": "input",
        "message": "What do you want",
        "completer": {
            "hello": None,
            "what": None,
            "hey": None,
            "whaa": None,
            "whaaa": None,
            "wheee": None,
        },
        "multicolumn_complete": True,
    },
    {
        "type": "input",
        "message": "What do you want",
        "multiline": True,
        "filter": lambda x: x * 2,
    },
]

result = prompt(questions, vi_mode=True)
print(result)
