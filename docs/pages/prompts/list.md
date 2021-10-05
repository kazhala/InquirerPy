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

## Choices

```{seealso}
{ref}`pages/dynamic:choices`
```

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

## Multiple Selection

```{seealso}
{ref}`pages/prompts/list:Keybindings`
```

You can enable multiple selection on the prompt by configuring the parameter `multiselect` to `True`.

You can also have certain choices pre-selected during the mode. The choices to be pre-selected requires to be either an instance
of {class}`~InquirerPy.base.control.Choice` or {class}`dict`.

The following example will have `1` and `2` pre-selected.

```{code-block} python
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

choices = [
    Choice(1, enabled=True),
    Choice(2, enabled=True),
    3,
    4,
]

result = inquirer.select(
    message="Selct one:", choices=choices, multiselect=True
).execute()
```

## Default Value

```{seealso}
{ref}`pages/dynamic:default`
```

The `default` parameter will be used to determine which choice is highlighted by default.

It should be the value of one of the choices.
