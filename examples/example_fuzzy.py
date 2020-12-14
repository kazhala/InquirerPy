from InquirerPy.resolver import prompt

questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": ["meat", "what", "whaaah", "weather", "haha"],
        "boarder": True,
        "multiselect": True,
    }
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
