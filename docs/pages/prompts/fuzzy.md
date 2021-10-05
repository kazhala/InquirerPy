# FuzzyPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.fuzzy.FuzzyPrompt
    :noindex:
```

## Example

```{note}
The following example will download a sample file and demos the performance of searching with 100k words.
```

![demo](https://assets.kazhala.me/InquirerPy/fuzzy.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/fuzzy.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/fuzzy.py
   :language: python
```

</details>

## Choices

```{seealso}
{ref}`pages/dynamic:choices`
```

```{attention}
This prompt does not accepts choices containing {ref}`pages/separator:Separator` instances.
```

## Keybindings

```{seealso}
{ref}`pages/prompts/list:keybindings`
```

It shares the same keybindings with other list prompts. The only caveat is that it does not enable `j/k` navigation
when `vi_mode` is True.

When `vi_mode` is True in fuzzy prompt, the input buffer will become vim input mode, no other keybindings are altered.

## Multiple Selection

```{seealso}
{ref}`pages/prompts/list:Multiple Selection`
```

## Default Value

```{seealso}
{ref}`pages/dynamic:default`
```

The `default` parameter for this prompt will set the default search text in the input buffer (sort of replicate the behavior of fzf).

If you wish to pre-select certain choices, you can leverage the `enabled` parameter/key of each choice.

```{code-block} python
from InquirerPy.base import Choice

choices = [
    Choice(1, enabled=True),  # enabled by default
    Choice(2)  # not enabled
]
```
