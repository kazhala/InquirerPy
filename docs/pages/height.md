# Height

```{attention}
Height configuration only applies to prompts that spans over multiple lines.

Prompts such as {ref}`pages/prompts/input:InputPrompt` and similar prompts that only uses 1 line
total space does not support height configuration.
```

```{tip}
For a better user experience, using the `max_height` parameter is preferred over `height`.

The `max_height` parameter allows the height of the prompt to be more dynamic, prompt will only take as much space
as it needs. When reaching the number specified via `max_height`, user will be able to scroll.
```

The total height of the prompt can be adjusted using the parameter `height` and `max_height`.

The value of both parameters can be either a {class}`int` or a {class}`str`. An {class}`int` indicates an exact value in how many
lines in the terminal the prompt should take (e.g. setting `height=1` will cause the prompt to only display 1 choice at a time).
A {class}`str` indicates a percentile in respect tot he entire visible terminal.

### `height`

The `height` parameter will set the prompt height to a fixed value no matter how much space the content requires.
The following example will only display 2 choices at a time, meaning only the choice 1 and 2 will be visible. The choice 3
will be visible when user scroll down.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
    {
        "type": "list",
        "message": "Select one:",
        "choices": [1, 2, 3],
        "default": 2,
        "height": 2
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    height=2
).execute()
```

</details>

The following example will take 50% of the entire terminal as its height.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
    {
        "type": "list",
        "message": "Select one:",
        "choices": [1, 2, 3],
        "default": 2,
        "height": "50%" # or "50" also works
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    height="50%" # or "50" also works
).execute()
```

</details>

### `max_height`

```{tip}
The default value for `max_height` is configured to be "70%" if not specified.
```

The `max_height` will set the prompt height to a dynamic value and will only stop increasing if the total height
reaches the specified `max_height` value.

The following example will let the prompt to display all of its content unless the visible terminal is less than 10 lines and
is not enough to display all 3 choices, then user will be able to scroll.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
    {
        "type": "list",
        "message": "Select one:",
        "choices": [1, 2, 3],
        "default": 2,
        "max_height": "50%" # or just "50"
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    max_height="50%" # or just "50"
).execute()
```

</details>
