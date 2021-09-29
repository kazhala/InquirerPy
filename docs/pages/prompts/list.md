# ListPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.list.ListPrompt
    :noindex:
```

## Example

![demo](https://assets.kazhala.me/InquirerPy/list.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/list.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/list.py
   :language: python
```

</details>

## Keybindings

```{seealso}
Checkout {ref}`pages/kb:Keybindings` documentation for information on how to customise the keybindings.
```

```{tip}
In addition to the following keybindings, you can use `c-c` to terminate the prompt and `enter` to answer the prompt.
```

The following dictionary contains the default keybindings for the prompt.

```{code-block} python
{
    "down": [
        {"key": "down"},
        {"key": "c-n"}, # ctrl-n
    ],
    "up": [
        {"key": "up"},
        {"key": "c-p"}, # ctrl-p
    ],
    # The following will only be active if multiselect is True
    "toggle": [
        {"key": "space"},
    ],
    "toggle-down": [
        {"key": "c-i"}, # tab
    ],
    "toggle-up": [
        {"key": "s-tab"}, # shift + tab
    ],
    "toggle-all": [
        {"key": "alt-r"},
    ],
    "toggle-all-true": [
        {"key": "alt-a"},
    ],
    "toggle-all-false": [],
}
```

When `vi_mode` is True, the "up" and "down" navigation key will be changed.

```{code-block} python
{
    "down": [
        {"key": "down"},
        {"key": "j"},
    ],
    "up": [
        {"key": "up"},
        {"key": "k"},
    ],
}
```

## Height

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

```{code-block} python
from InquirerPy import inquirer

result = inquirer.list(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    height=2
).execute()
```

The following example will take 50% of the entire terminal as its height.

```{code-block} python
from InquirerPy import inquirer

result = inquirer.list(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    height="50%" # or "50" also works
).execute()
```

### `max_height`

```{tip}
The default value for `max_height` is configured to be "70%" if not specified.
```

The `max_height` will set the prompt height to a dynamic value and will only stop increasing if the total height
reaches the specified `max_height` value.

The following example will let the prompt to display all of its content unless the visible terminal is less than 10 lines and
is not enough to display all 3 choices, then user will be able to scroll.

```{code-block} python
from InquirerPy import inquirer

result = inquirer.list(
    message="Select one:",
    choices=[1, 2, 3],
    default=2,
    max_height="50%" # or just "50"
).execute()
```
