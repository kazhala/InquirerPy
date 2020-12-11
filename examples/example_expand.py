from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "expand",
        "options": [
            {"key": "j", "name": "Jump", "value": "Jump"},
            {"key": "y", "name": "Yes", "value": "No"},
        ],
        "question": "What do you think?",
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
    },
]

result = prompt(questions)
print(result)
