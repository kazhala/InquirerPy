from InquirerPy import prompt

questions = [
    {
        "type": "confirm",
        "name": "hello",
        "question": "Proceed?",
        "default": True,
        "symbol": "?",
    },
    {
        "type": "confirm",
        "name": "foo",
        "question": "Are you sure?",
        "condition": lambda result: result["hello"] == True,
    },
]

print(prompt(questions))
