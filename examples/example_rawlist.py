from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "rawlist",
        "options": ["hello", "world", "foo", "boo"],
        "message": "Select one of them",
        "default": "boo",
        "symbol": "[?]",
        "pointer": "   ",
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
        "message": "Select things apply",
        "default": 3,
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
