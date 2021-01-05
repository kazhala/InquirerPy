from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator


def hello(_):
    return [
        {"key": "1", "name": "1", "value": 1},
        {"key": "2", "name": "2", "value": 2},
        {"key": "3", "name": "3", "value": 3},
    ]


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
        "multiselect": True,
        "keybindings": {"up": [{"key": "c-p"}], "down": [{"key": "c-n"}]},
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
    {"type": "expand", "choices": hello, "message": "What"},
]

result = prompt(
    questions,
    vi_mode=True,
)
print(result)
