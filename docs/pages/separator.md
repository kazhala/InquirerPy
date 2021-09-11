# Separator

You can use {class}`~InquirerPy.separator.Separator` to effectively group choices visually in the
following types of prompts which involves list of choices:

- {ref}`pages/prompts/list:list`
- {ref}`pages/prompts/rawlist:rawlist`
- {ref}`pages/prompts/expand:expand`
- {ref}`pages/prompts/checkbox:checkbox`

```{eval-rst}
.. autoclass:: InquirerPy.separator.Separator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
"""
? Select regions: █
  Sydney
❯ Singapore
  ---------------   <- Separator
  us-east-1
  us-east-2
"""
from InquirerPy import prompt
from InquirerPy.separator import Separator

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select regions:",
            "choices": [
                {"name": "Sydney", "value": "ap-southeast-2"},
                {"name": "Singapore", "value": "ap-southeast-1"},
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            "multiselect": True,
            "transformer": lambda result: "%s region%s selected"
            % (len(result), "s" if len(result) > 1 else ""),
        },
    ],
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
"""
? Select regions: █
  Sydney
❯ Singapore
  ---------------   <- Separator
  us-east-1
  us-east-2
"""
from InquirerPy import inquirer
from InquirerPy.separator import Separator

region = inquirer.select(
    message="Select regions:",
    choices=[
        {"name": "Sydney", "value": "ap-southeast-2"},
        {"name": "Singapore", "value": "ap-southeast-1"},
        Separator(),
        "us-east-1",
        "us-east-2",
    ],
    multiselect=True,
    transformer=lambda result: "%s region%s selected"
    % (len(result), "s" if len(result) > 1 else ""),
).execute()
```

</details>
