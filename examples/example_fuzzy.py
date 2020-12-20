from pathlib import Path

from InquirerPy.resolver import prompt

p = Path("~/Programming/shell/dotbare/tests").expanduser()
paths = []
for path in p.rglob("*"):
    paths.append(path)
paths = paths * 20

questions = [
    {
        "type": "fuzzy",
        "message": "Select one of them",
        "choices": paths,
        "border": True,
        "multiselect": True,
        "max_height": "100%",
        "validate": lambda x: len(x) > 1,
    }
]

result = prompt(questions=questions, editing_mode="vim")
print(result)
