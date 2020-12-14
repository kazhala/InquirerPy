from InquirerPy.resolver import prompt

questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": ["meat", "what", "whaaah", "weather", "haha"],
        "border": True,
        "multiselect": True,
        "max_height": "100%",
    }
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
