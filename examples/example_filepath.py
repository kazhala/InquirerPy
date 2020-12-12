from pathlib import Path

from InquirerPy.resolver import prompt
from InquirerPy.validator import PathValidator

questions = [
    {
        "type": "filepath",
        "message": "Select file to upload",
        "invalid_message": "Input is not a valid filepath",
        "name": "location",
        "default": str(Path.cwd()),
        "validate": PathValidator(),
        "only_directories": True,
    },
    {
        "type": "filepath",
        "message": "Select path to store",
        "validate": None,
        "name": "destination",
        "symbol": "[?]",
        "validate": lambda x: x != "",
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
