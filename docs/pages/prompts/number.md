# number

A prompt for entering numbers. All non number input will be disabled for this prompt.

## Example

![demo](https://assets.kazhala.me/InquirerPy/number.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/number.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/number.py
   :language: python
```

</details>

## Keybindings

```{seealso}
{ref}`pages/kb:Keybindings`
```

```{include} ../kb.md
:start-after: <!-- start kb -->
:end-before: <!-- end kb -->
```

The following dictionary contains the additional keybindings created by this prompt.

```
{
  "down": [
    {"key": "down"},  # decrement the number
    {"key": "c-n"},
  ],
  "up": [
    {"key": "up"},  # increment the number
    {"key": "c-p"},
  ],
  "left": [
    {"key": "left"},  # move cursor to the left
    {"key": "c-b"},
  ],
  "right": [
    {"key": "right"},   # move cursor to the right
    {"key": "c-f"},
  ],
  "focus": [
    {"key": "c-i"},   # focus the alternate input buffer when float_allowed=True
    {"key": "s-tab"},
  ],
  "negative_toggle": [{"key": "-"}], # toggle result negativity
}
```

When `vi_mode` is True, the direction navigation key will be changed.

```{tip}
Additionally, the input buffer can also enter normal mode by pressing `esc` when `vi_mode` is True.
```

```
{
  "down": [
    {"key": "down"},
    {"key": "j"},
  ],
  "up": [
    {"key": "up"},
    {"key": "k"},
  ],
  "left": [
    {"key": "left"},
    {"key": "h"},
  ],
  "right": [
    {"key": "right"},
    {"key": "l"},
  ],
}
```

## Max and Min

You can set the maximum allowed value as well as the minimum allowed value for the prompt via `max_allowed` and `min_allowed`.

```{hint}
When the input value goes above/below the max/min value, the input value will automatically reset to the
configured max/min value.
```

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
  {
    "type": "number",
    "message": "Number:",
    "max_allowed": 10,
    "min_allowed": -100
  }
]

result = prompt(questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.number(
  message="Number:", max_allowed=10, min_allowed=-100,
).execute()
```

</details>

## Decimal Input

```{tip}
Once you enable decimal input, the prompt will have a second input buffer. You can keep navigating `left`/`right`
to enter the other input buffer or you can use the `tab`/`shit-tab` to focus the other buffer.
```

You can enable decimal input by setting the argument `float_allowed` to True.

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
  {
    "type": "number",
    "message": "Number:",
    "float_allowed": True
  }
]

result = prompt(questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

result = inquirer.number(
  message="Number:", float_allowed=True,
).execute()
```

</details>

## Reference

```{eval-rst}
.. autoclass:: InquirerPy.prompts.number.NumberPrompt
    :noindex:
```
