from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "rawlist",
        "choices": ["hello", "world", "foo", "boo"],
        "message": "Select one of them",
        "default": "boo",
        "qmark": "[?]",
        "pointer": "   ",
    },
    {
        "type": "rawlist",
        "choices": [
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
        "multiselect": True,
        "validate": lambda x: len(x) > 1,
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
