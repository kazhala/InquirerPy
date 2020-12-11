from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "expand",
        "options": [
            {"key": "j", "name": "Jump", "value": "Jump"},
            {"key": "y", "name": "Yes", "value": "No"},
            {"key": "w", "name": "Word", "value": "HAHAHA"},
        ],
        "question": "What do you think?",
        "default": "No",
    },
    {
        "type": "expand",
        "options": [
            Separator(),
            {"name": "hello", "value": "world", "key": "b"},
            Separator("**********"),
            {"name": "foo", "value": "boo", "key": "f"},
        ],
        "question": "What do you think?",
        "default": "f",
    },
]

result = prompt(questions)
print(result)
