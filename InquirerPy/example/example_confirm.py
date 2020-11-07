from InquirerPy import prompt


questions = [
    {
        "type": "confirm",
        "name": "hello",
        "question": "adfasfadsfasd",
        "default_true": False,
        "symbol": "x",
    }
]

print(prompt(questions))
