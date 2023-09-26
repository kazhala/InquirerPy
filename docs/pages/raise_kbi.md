# Skip & KeyboardInterrupt

Prior to version `0.3.0`, the parameter `raise_keyboard_interrupt` can control whether to raise the exception
{class}`KeyboardInterrupt` when user hit `ctrl-c` or let `InquirerPy` handle the exception which will skip the prompt when
user hit `ctrl-c`. However this would cause issues when user actually want to terminate the program and also will have some side effects
if future prompts depends on the result.

With the release of `0.3.0`, dedicated skipping functionality is introduced along with the parameter `mandatory` which
is used to indicate if a prompt is skippable. The parameter [raise_keyboard_interrupt](#raise-keyboard-interrupt) also behaves a little different than before.

## Skip

```{important}
All prompts are mandatory and cannot be skipped by default.
```

````{note}
Default keybinding for skip is `ctrl-z`.

```{seealso}
{ref}`pages/kb:Default Keybindings`
```
````

When `mandator=False` for a prompt, user will be able to skip the prompt. In the case of a skip attempt when
`mandatory=True`, an error message will be displayed using the parameter `mandatory_message="Mandatory prompt"`.

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
            "mandatory": False,
        },
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
            "mandatory": True,
            "mandatory_message": "Cannot skip"
        },
    ],
    vi_mode=True,
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    vi_mode=True,
    mandatory=False,
).execute()
result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    vi_mode=True,
    mandatory=True,
    mandatory_message="Cannot skip",
).execute()
```

</details>

## KeyboardInterrupt

````{note}
Default keybinding for terminating the program with KeyboardInterrupt is `ctrl-c`.

```{seealso}
{ref}`pages/kb:Default Keybindings`
```
````

There are multiple ways you can control how {class}`KeyboardInterrupt` is raised.

### keybindings

```{seealso}
{ref}`pages/kb:Customising Keybindings`
```

You can directly change the keybinding for raising {class}`KeyboardInterrupt` using the `keybindings` parameter.

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
            "mandatory_message": "Prompt is mandatory, terminate the program using ctrl-d",
        },
    ],
    keybindings={"skip": [{"key": "c-c"}], "interrupt": [{"key": "c-d"}]},
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    mandatory_message="Prompt is mandatory, terminate the program using ctrl-d",
    keybindings={"skip": [{"key": "c-c"}], "interrupt": [{"key": "c-d"}]},
).execute()
```

</details>

### raise_keyboard_interrupt

```{warning}
If you are already customising `skip` and `interrupt` using [keybindings](#keybindings) parameter, avoid using
[raise_keyboard_interrupt](#raise-keyboard-interrupt) since it also attempts to change `skip` and `interrupt`.
```

```{tip}
`raise_keyboard_interrupt` is basically a managed way of customising keybindings similar to parameter `vi_mode`.
```

```{tip}
It'd be helpful inform the user how to terminate the program using the parameter `long_instruction` or `mandatory_message`.
```

If you prefer to have a keybinding style like Python REPL (e.g. `ctrl-c` to skip the prompt and `ctrl-d` to terminate the program),
you can leverage the parameter `raise_keyboard_interrupt`.

When `raise_keyboard_interrupt` is set to False:

- `ctrl-c` will be binded to skip the prompt
- `ctrl-d` can be used to raise {class}`KeyboardInterrupt`

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
            "mandatory_message": "Prompt is mandatory, terminate the program using ctrl-d",
        },
    ],
    raise_keyboard_interrupt=False,
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    raise_keyboard_interrupt=False,
    mandatory_message="Prompt is mandatory, terminate the program using ctrl-d",
).execute()
```

</details>
