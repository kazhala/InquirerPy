from pathlib import Path

from InquirerPy.resolver import prompt

questions = [
    {
        "type": "filepath",
        "question": "Select file to upload",
        "invalid_message": "Input is not a valid filepath",
        "name": "location",
        "default": str(Path.cwd()),
    },
    {
        "type": "filepath",
        "question": "Select path to store",
        "validator": None,
        "name": "destination",
        "symbol": "[?]",
    },
]

result = prompt(questions)
print(result)
