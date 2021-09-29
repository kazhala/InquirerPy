# Dynamic Values

Several parameters across different prompts accepts callable/function as the argument which
allows you to perform additional logic and generate the argument dynamically.

There's mainly two categories: [Before Rendered](#before-rendered) and [After Answered](#after-answered).

## Before Rendered

Parameters/Keys in this category will be retrieved before the prompt is displayed in the terminal. The main purpose of this category
is to allow {ref}`index:Classic Syntax (PyInquirer)` users to customise the prompt based on previous prompts result.

When these parameters/keys receive function/callable as an argument, the current `InquirerPySessionResult` will be provided as an argument and you can
perform additional logic to generate and return different values.

### Classic Syntax (PyInquirer)

Let's take the `message` and `default` key as an example, in certain scenario, you may want to display different `message` and obtain different `default` values based on previous prompts result.

In the following example, the second prompt will set the `default` value based on the result from the first prompt. And the third prompt will display the `message` based on the result from second prompt.

```python
from InquirerPy import prompt
from InquirerPy.validator import NumberValidator

def get_message(result):
    return f"Hi {result['confirm_name']}, enter your age:"

questions = [
    {
        "type": "input",
        "message": "Name:",
        "name": "name",
    },
    {
        "type": "input",
        "message": "Confirm Name:",
        "name": 'confirm_name',
        "default": lambda result: result["name"],   # inline lambda to make the code shorter
    },
    {
        "type": "input",
        "message": get_message,   # use a named function for more complex logic
        "name": 'age',
        "validate": NumberValidator(),
    },
]

result = prompt(questions)
```

### Alternate Syntax

When using {ref}`pages/inquirer:inquirer`, you will receive the result immediately after the prompt execution. Hence you can directly
perform your logic to generate the parameters dynamically after each prompt execution.

```
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

name = inquirer.text(message="Name:").execute()
confirm_name = inquirer.text(message="Confirm Name:", default=name).execute()
age_message = f"Hi {confirm_name}, enter your age:"
age = inquirer.text(message=age_message, validate=NumberValidator()).execute()
```

However for the sake of keeping code shorter and cleaner in certain scenarios, you can also provide applicable parameters with a function/callable.

```{attention}
To maintain API compatibility with [Classic Syntax](#classic-syntax-pyinquirer), the function will also receive an argument, however it will be `None`. To make your linter/IDE
happy, you should put a dummy parameter `_` in your function definition.

There are plans in place to remove the need of adding dummy parameter in future.
```

```{note}
The following is not a good example that make the code shorter or cleaner..but it just simply illustrate an alternate way of passing arguments.
```

```python
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

name = inquirer.text(message="Name:").execute()
confirm_name = inquirer.text(message="Confirm Name:", default=lambda _:name).execute()
age = inquirer.text(
    message=lambda _: f"Hi {name}, enter your age:", validate=NumberValidator()
).execute()
```

### Parameters/Keys

#### message

```{eval-rst}
.. autodata:: InquirerPy.utils.InquirerPyMessage
    :noindex:
```

```{admonition} Category
[Before Rendered](#before-rendered)
```

```{seealso}
[Classic Syntax Example](#classic-syntax-pyinquirer)

[Alternate Syntax Example](#alternate-syntax)
```

The `message` parameter/key can either be a simple {class}`string` or a function which returns {class}`string`.

#### default

```{eval-rst}
.. autodata:: InquirerPy.utils.InquirerPyDefault
    :noindex:
```

```{admonition} Category
[Before Rendered](#before-rendered)
```

```{attention}
The `default` parameter/key typing can vary between different types of prompt.
```

```{seealso}
[Classic Syntax Example](#classic-syntax-pyinquirer)

[Alternate Syntax Example](#alternate-syntax)
```

The `default` parameter/key can either be a simple value or a function which returns the `default` value.

#### choices

```{eval-rst}
.. autodata:: InquirerPy.utils.InquirerPyListChoices
    :noindex:
```

```{admonition} Category
[Before Rendered](#before-rendered)
```

```{attention}
This variable only exists in the following prompts:

* {ref}`pages/prompts/list:ListPrompt`,
* {ref}`pages/prompts/rawlist:RawlistPrompt`,
* {ref}`pages/prompts/expand:ExpandPrompt`,
* {ref}`pages/prompts/checkbox:CheckboxPrompt`,
* {ref}`pages/prompts/fuzzy:FuzzyPrompt`
```

```{note}
The required keys for choices vary between prompts. There may be additional keys required which is documented
in individual prompt documentation.
```

Each choice can be either any value that have a string representation (e.g. can `str(value)`), or it can be a
dictionary which consists at least the following keys:

- name (Any): The display name of the choice, user will be able to see this value as the choice.
- value (Any): The value of the choice, can be different than the `name` key, user will not be able to see this value.

Choice can also be instances of {ref}`pages/separator:Separator`.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt
from InquirerPy.separator import Separator

questions = [
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
        "transformer": lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
    },
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
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
    transformer=lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
).execute()
```

</details>

## After Answered

Parameters/Keys in this category will be retrieved after the question is answered. The main purpose of this category is to allow additional customisation
to the appearance of the prompt based on user answer after the prompt is answered.

### Parameters/Keys

#### filter

```
Callable[[Any], Any]
```

```{admonition} Category
[After Answered](#after-answered)
```

```{tip}
For prompts that accepts parameter `choices`, the value provided to the filter function will be the value
of the selected choice (`choice["value"]`) or a list of values of the selected choices.
```

A function which performs additional transformation on the result. This affects the actual value returned by {meth}`~InquirerPy.base.simple.BaseSimplePrompt.execute`.

Leveraging this parameter/key can potentially shorten the code and create a cleaner code base. Given a scenario you want to obtain the age from the user, however the result
from {ref}`pages/prompts/input:InputPrompt` is type of {class}`string` by default. You can use the `filter` parameter/key to convert them to {class}`int`.

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import NumberValidator

questions = [
    {
        "type": "input",
        "message": "Age:",
        "filter": lambda result: int(result),
        "validate": NumberValidator()
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

age = inquirer.text(
    message="Age:", filter=lambda result: int(result), validate=NumberValidator()
).execute()
```

</details>

#### transformer

```
Callable[[Any], str]
```

```{admonition} Category
[After Answered](#after-answered)
```

```{note}
The value received by `transformer` will always be either type of {class}`str` or {class}`list` of {class}`str` depending on the prompt types.
```

```{tip}
`filter` and `transformer` run separately and won't have side effects when running both.
```

```{tip}
For prompts that accepts parameter `choices`, the value provided to the transformer function will be the name
of the selected choice (`choice["name"]`) or a list of names of the selected choices.
```

A function which performs additional transformation on the value that gets printed to the terminal.
Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by {meth}`~InquirerPy.base.simple.BaseSimplePrompt.execute`.

For example, when working with {ref}`pages/prompts/checkbox:CheckboxPrompt`, all user selected choices will be displayed in the terminal. This may create
unnecessary clutter of texts and may cause the displayed information become less useful. You can use `transformer` parameter/key to change how the result will be printed.

<details>
  <summary>Classic Syntax</summary>

```python
"""
Without transformer: ? Select regions: ["us-east-1", "us-west-1"]
With transformer: ? Select regions: 2 regions selected
"""
from InquirerPy import prompt

choices = [
    {"name": "Sydney", "value": "ap-southeast-2", "enabled": True},
    {"name": "Singapore", "value": "ap-southeast-1", "enabled": False},
    "us-east-1",
    "us-west-1",
]

questions = [
    {
        "type": "checkbox",
        "message": "Select regions:",
        "choices": choices,
        "cycle": False,
        "transformer": lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
"""
Without transformer: ? Select regions: ["us-east-1", "us-west-1"]
With transformer: ? Select regions: 2 regions selected
"""
from InquirerPy import inquirer

choices = [
    {"name": "Sydney", "value": "ap-southeast-2", "enabled": True},
    {"name": "Singapore", "value": "ap-southeast-1", "enabled": False},
    "us-east-1",
    "us-west-1",
]

regions = inquirer.checkbox(
    message="Select regions:",
    choices=choices,
    cycle=False,
    transformer=lambda result: f"{len(result)} region{'s' if len(result) > 1 else ''} selected",
).execute()
```

</details>
