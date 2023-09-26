# select

A prompt that displays a list of choices to select.

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
{ref}`pages/kb:Keybindings`
```

```{include} ../kb.md
:start-after: <!-- start kb -->
:end-before: <!-- end kb -->
```

<!-- start list kb -->

The following dictionary contains the additional keybindings created by this prompt.

```{code-block} python
{
    "down": [
        {"key": "down"},
        {"key": "c-n"},   # move down
    ],
    "up": [
        {"key": "up"},
        {"key": "c-p"},   # move up
    ],
    "toggle": [
        {"key": "space"},   # toggle choices
    ],
    "toggle-down": [
        {"key": "c-i"},   # toggle choice and move down (tab)
    ],
    "toggle-up": [
        {"key": "s-tab"},   # toggle choice and move up (shift+tab)
    ],
    "toggle-all": [
        {"key": "alt-r"},   # toggle all choices
        {"key": "c-r"},
    ],
    "toggle-all-true": [
        {"key": "alt-a"},   # toggle all choices true
        {"key": "c-a"}.
    ],
    "toggle-all-false": [],   # toggle all choices false
}
```

<!-- end list kb -->

<!-- start list vi kb -->

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

<!-- end list vi kb -->

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
    message="Select one:", choices=choices, multiselect=True
).execute()
```

## Default Value

```{seealso}
{ref}`pages/dynamic:default`
```

The `default` parameter will be used to determine which choice is highlighted by default.

It should be the value of one of the choices.

If you wish to pre-select certain choices in multiselect mode, you can leverage the `enabled` parameter/key of each choice.

```{code-block} python
from InquirerPy.base import Choice

choices = [
    Choice(1, enabled=True),  # enabled by default
    Choice(2)  # not enabled
]
```

## Reference

```{eval-rst}
.. autoclass:: InquirerPy.prompts.list.ListPrompt
    :noindex:
```
