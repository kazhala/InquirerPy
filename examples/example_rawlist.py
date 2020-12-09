from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "rawlist",
        "options": ["hello", "world", "foo", "boo"],
        "question": "Select one of them",
        "default": "boo",
    },
    {
        "type": "rawlist",
        "options": [
            {"name": "foo", "value": "boo"},
            "hello",
            Separator(),
            Separator(),
            "yes",
            Separator(),
            "blah",
        ],
        "question": "Select things apply",
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
