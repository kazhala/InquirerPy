from InquirerPy.resolver import prompt
from InquirerPy.separator import Separator

questions = [
    {
        "type": "checkbox",
        "question": "Select which applies",
        "options": [
            "boy",
            "girl",
            Separator(),
            {"name": "mix", "value": "boy&girl", "enabled": True},
        ],
    },
    {
        "name": "nba",
        "type": "checkbox",
        "question": "Select players you want",
        "options": [
            {"name": "Chris Paul", "value": "pg"},
            {"name": "Kobe, Bryant", "value": "sg"},
            {"name": "Lebron James", "value": "sf"},
            {"name": "Tim Duncan", "value": "pf"},
            {"name": "Yao Ming", "value": "c"},
        ],
        "pointer": ">",
        "symbol": "[?]",
    },
]

result = prompt(questions, editing_mode="vim")
print(result)
