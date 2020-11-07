from InquirerPy import prompt


questions = [
    {
        "type": "confirm",
        "name": "hello",
        "question": "adfasfadsfasd",
        "default_true": True,
    }
]

print(prompt(questions))
