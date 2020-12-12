from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "expand",
        "choices": [
            {"key": "j", "name": "Jump", "value": "Jump"},
            {"key": "y", "name": "Yes", "value": "No"},
            {"key": "w", "name": "Word", "value": "HAHAHA"},
        ],
        "message": "What do you think?",
        "default": "No",
    },
    {
        "type": "expand",
        "choices": [
            Separator(),
            {"name": "hello", "value": "world", "key": "b"},
            Separator("**********"),
            {"name": "foo", "value": "boo", "key": "f"},
        ],
        "message": "What do you think?",
        "default": "f",
    },
]

result = prompt(questions)
print(result)
