# CheckboxPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.checkbox.CheckboxPrompt
    :noindex:
```

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
{ref}`pages/prompts/list:Keybindings`
```

## Default Value

```{seealso}
{ref}`pages/prompts/list:Default Value`
```
