from InquirerPy.resolver import prompt

questions = [
    {
        "type": "list",
        "question": "Select a fruit",
        "options": [{"name": "banana", "value": "peach"}, "apple", "orange"],
        "default": "apple",
    }
]

result = prompt(questions=questions)
print(result)
