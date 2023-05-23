# Validator

All `InquirerPy` prompts can validate user input and display an error toolbar when the input or selection is invalid.

## Parameters

Each prompt accepts two parameters for validation: [validate](#validate) and [invalid_message](#invalid_message).

Below is an example of ensuring the user doesn't by pass an empty input.

<details>
  <summary>Classic Syntax</summary>

```{code-block} python
from InquirerPy import prompt

result = prompt(
    [
        {
            "type": "input",
            "message": "Name:",
            "validate": lambda result: len(result) > 0,
            "invalid_message": "Input cannot be empty.",
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.text(
    message="Name:",
    validate=lambda result: len(result) > 0,
    invalid_message="Input cannot be empty.",
).execute()
```

</details>

Below is another example which ensure that at least 2 options are checked.

<details>
  <summary>Classic Syntax</summary>

```{code-block} python
from InquirerPy import prompt

result = prompt(
    [
        {
            "type": "list",
            "message": "Select toppings:",
            "choices": ["Bacon", "Chicken", "Cheese", "Pineapple"],
            "multiselect": True,
            "validate": lambda selection: len(selection) >= 2,
            "invalid_message": "Select at least 2 toppings.",
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.checkbox(
    message="Select toppings:",
    choices=["Bacon", "Chicken", "Cheese", "Pineapple"],
    validate=lambda selection: len(selection) >= 2,
    invalid_message="Select at least 2 toppings.",
).execute()
```

</details>

### validate

```
Union[Callable[[Any], bool], "Validator"]
```

Validation callable or class to validate user input.

#### Callable

```{note}
The `result` provided will vary depending on the prompt types. E.g. `checkbox` prompt will receive a list of checked choices as the result.
```

When providing validate as a {func}`callable`, it will be provided with the current user input and should return a boolean
indicating if the input is valid.

```python
def validator(result) -> bool:
    """Ensure the input is not empty."""
    return len(result) > 0
```

#### prompt_toolkit.validation.Validator

```{note}
To maintain API compatibility, for prompts that doesn't have a {class}`string` type result such as `checkbox`, you'll still need to access the result via `document.text`.
```

You can also provide a `prompt_toolkit` {class}`~prompt_toolkit.validation.Validator` instance.

This method removes the need of providing the `invalid_message` parameter.

```python
from prompt_toolkit.validation import ValidationError, Validator

class EmptyInputValidator(Validator):
    def validate(self, document):
        if not len(document.text) > 0:
            raise ValidationError(
                message="Input cannot be empty.",
                cursor_position=document.cursor_position,
            )
```

### invalid_message

```
str
```

The error message you would like to display to user when the input is invalid.

## Pre-built Validators

There's a few pre-built common validator ready to use.

### PathValidator

```{eval-rst}
.. autoclass:: InquirerPy.validator.PathValidator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import PathValidator

result = prompt(
    [
        {
            "type": "filepath",
            "message": "Enter path:",
            "validate": PathValidator("Path is not valid"),
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

result = inquirer.filepath(message="Enter path:", validate=PathValidator()).execute()
```

</details>

### EmptyInputValidator

```{eval-rst}
.. autoclass:: InquirerPy.validator.EmptyInputValidator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import EmptyInputValidator

result = prompt(
    [{"type": "input", "message": "Name:", "validate": EmptyInputValidator()}]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

result = inquirer.text(
    message="Name:", validate=EmptyInputValidator("Input should not be empty")
).execute()
```

</details>

### PasswordValidator

```{eval-rst}
.. autoclass:: InquirerPy.validator.PasswordValidator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import PasswordValidator

result = prompt(
    [
        {
            "type": "secret",
            "message": "New Password:",
            "validate": PasswordValidator(
                length=8,
                cap=True,
                special=True,
                number=True,
                message="Password does not meet compliance",
            ),
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import PasswordValidator

result = inquirer.secret(
    message="New Password:",
    validate=PasswordValidator(
        length=8,
        cap=True,
        special=True,
        number=True,
        message="Password does not meet compliance",
    ),
).execute()
```

</details>

### NumberValidator

```{eval-rst}
.. autoclass:: InquirerPy.validator.NumberValidator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import NumberValidator

result = prompt(
    [
        {
            "type": "text",
            "message": "Age:",
            "validate": NumberValidator(
                message="Input should be number", float_allowed=False
            ),
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

result = inquirer.text(message="Age:", validate=NumberValidator()).execute()
```

</details>

### DateValidator

```{eval-rst}
.. autoclass:: InquirerPy.validator.DateValidator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy.validator import DateValidator

result = prompt(
    [
        {
            "type": "input",
            "message": "Date of birth:",
            "validate": DateValidator(
                message="Invalid date format",
                formats=["%Y-%m-%d"]
            ),
        }
    ]
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

result = inquirer.text(message="Date of birth:", validate=DateValidator()).execute()
```

</details>