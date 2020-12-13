from InquirerPy.resolver import prompt

questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": ["meat", "what", "whaaah", "weather", "haha"],
    }
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
