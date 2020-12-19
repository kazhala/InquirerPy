from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "checkbox",
        "message": "Select which applies",
        "choices": [
            "boy",
            "girl",
            Separator(),
            {"name": "mix", "value": "boy&girl", "enabled": True},
        ],
    },
    {
        "name": "nba",
        "type": "checkbox",
        "message": "Select players you want:",
        "choices": [
            {"name": "Chris Paul", "value": "pg"},
            {"name": "Kobe Bryant", "value": "sg"},
            {"name": "Lebron James", "value": "sf"},
            {"name": "Tim Duncan", "value": "pf"},
            {"name": "Yao Ming", "value": "c"},
        ],
        "pointer": ">",
        "qmark": "[?]",
        "validate": lambda x: len(x) > 1,
        "invalid_message": "selection require to be more than 1",
        "instruction": "(select at least 2 values)",
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
