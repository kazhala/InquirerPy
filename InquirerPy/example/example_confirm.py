from InquirerPy import prompt


questions = [
    {
        "type": "confirm",
        "name": "hello",
        "question": "Proceed?",
        "default": True,
        "symbol": "?",
    }
]

print(prompt(questions))
