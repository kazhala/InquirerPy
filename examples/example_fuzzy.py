from InquirerPy.resolver import prompt

questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": ["meat", "what", "whaaah", "weather", "haha"],
        "border": True,
        "multiselect": True,
        "max_height": "100%",
        "validate": lambda x: len(x) > 1,
    }
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
