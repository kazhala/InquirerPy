from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "list",
        "message": "Select a fruit:",
        "choices": [{"name": "banana", "value": "peach"}, "apple", "orange"],
        "default": "apple",
        "multiselect": True,
    },
    {
        "type": "list",
        "message": "Select a sport:",
        "choices": [
            {"name": "Basketball", "value": "NBA"},
            {"name": "Rugby", "value": "NFL"},
            Separator(),
            "Soccer",
        ],
        "default": "apple",
        "filter": lambda x: "%s888888" % x,
    },
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
