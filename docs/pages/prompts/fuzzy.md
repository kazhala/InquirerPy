# fuzzy

A prompt that lists choices to select while also allowing fuzzy search like fzf.

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
{ref}`pages/kb:Keybindings`
```

```{hint}
This prompt does not enable `j/k` navigation when `vi_mode` is `True`. When `vi_mode` is `True` in fuzzy prompt, the input buffer
will become vim input mode, no other keybindings are altered.

The `space` key for toggle choice is also disabled since it blocks user from typing space in the input buffer.
```

```{include} ../kb.md
:start-after: <!-- start kb -->
:end-before: <!-- end kb -->
```

```{include} ./list.md
:start-after: <!-- start list kb -->
:end-before: <!-- end list kb -->
```

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

## Exact Sub-String Match

This prompt uses the [fzy](https://github.com/jhawthorn/fzy) fuzzy match algorithm by default. You can enable exact sub-string match
by using the parameter `match_exact`.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
    {
        "type": "fuzzy",
        "message": "Select actions:",
        "choices": ["hello", "weather", "what", "whoa", "hey", "yo"],
        "match_exact": True,
        "exact_symbol": " E",   # indicator of exact match
    },
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.fuzzy(
    message="Select actions:",
    choices=["hello", "weather", "what", "whoa", "hey", "yo"],
    match_exact=True,
    exact_symbol=" E",  # indicator of exact match
).execute()
```

</details>

## Reference

```{eval-rst}
.. autoclass:: InquirerPy.prompts.fuzzy.FuzzyPrompt
    :noindex:
```
