from pathlib import Path

from InquirerPy.resolver import prompt
from InquirerPy.validator import PathValidator

questions = [
    {
        "type": "filepath",
        "question": "Select file to upload",
        "invalid_message": "Input is not a valid filepath",
        "name": "location",
        "default": str(Path.cwd()),
        "validator": PathValidator(),
        "only_directories": True,
    },
    {
        "type": "filepath",
        "question": "Select path to store",
        "validator": None,
        "name": "destination",
        "symbol": "[?]",
        "validator": lambda x: x != "",
        "editing_mode": "vim",
    },
]

result = prompt(questions)
print(result)
