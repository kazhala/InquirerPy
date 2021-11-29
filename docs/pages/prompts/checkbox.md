# checkbox

A prompt which displays a list of checkboxes to toggle/tick.

## Example

![demo](https://assets.kazhala.me/InquirerPy/checkbox.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/checkbox.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/checkbox.py
   :language: python
```

</details>

## Choices

```{seealso}
{ref}`pages/dynamic:choices`
```

In checkbox prompt, the `multiselct` option is always enabled. If you want any choices to be pre-selected,
use {class}`~InquirerPy.base.control.Choice` to create choices and set `enabled` to True.

```{code-block} python
from InquirerPy.base import Choice

choices = [
    Choice("selected", enabled=True),
    Choice("notselected", enabled=False),
    "notselected2"
]
```

## Keybindings

```{seealso}
{ref}`pages/kb:Keybindings`
```

```{include} ../kb.md
:start-after: <!-- start kb -->
:end-before: <!-- end kb -->
```

```{include} ./list.md
:start-after: <!-- start list kb -->
:end-before: <!-- end list kb -->
```

```{include} ./list.md
:start-after: <!-- start list vi kb -->
:end-before: <!-- end list vi kb -->
```

## Default Value

```{seealso}
{ref}`pages/dynamic:default`
```

The `default` parameter will be used to determine which choice is highlighted by default.

It should be the value of one of the choices.

If you wish to pre-select certain choices, you can leverage the `enabled` parameter/key of each choice.

```{code-block} python
from InquirerPy.base import Choice

choices = [
    Choice(1, enabled=True),  # enabled by default
    Choice(2)  # not enabled
]
```

## Reference

```{eval-rst}
.. autoclass:: InquirerPy.prompts.checkbox.CheckboxPrompt
    :noindex:
```
