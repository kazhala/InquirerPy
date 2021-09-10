# Misc

## Separator

You can use {class}`~InquirerPy.separator.Separator` to effectively group choices visually in the
following types of prompts which involves list of choices:

- {class}`~InquirerPy.prompts.list.ListPrompt`
- {class}`~InquirerPy.prompts.rawlist.RawlistPrompt`
- {class}`~InquirerPy.prompts.expand.ExpandPrompt`
- {class}`~InquirerPy.prompts.checkbox.CheckboxPrompt`

```{eval-rst}
.. autoclass:: InquirerPy.separator.Separator
    :noindex:
```

<details>
  <summary>Classic Syntax</summary>

```python
"""
? Select regions: █
  Sydney
❯ Singapore
  ---------------
  us-east-1
  us-east-2
"""
from InquirerPy import prompt
from InquirerPy.separator import Separator

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select regions:",
            "choices": [
                {"name": "Sydney", "value": "ap-southeast-2"},
                {"name": "Singapore", "value": "ap-southeast-1"},
                Separator(),
                "us-east-1",
                "us-east-2",
            ],
            "multiselect": True,
            "transformer": lambda result: "%s region%s selected"
            % (len(result), "s" if len(result) > 1 else ""),
        },
    ],
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
"""
? Select regions: █
  Sydney
❯ Singapore
  ---------------
  us-east-1
  us-east-2
"""
from InquirerPy import inquirer
from InquirerPy.separator import Separator

region = inquirer.select(
    message="Select regions:",
    choices=[
        {"name": "Sydney", "value": "ap-southeast-2"},
        {"name": "Singapore", "value": "ap-southeast-1"},
        Separator(),
        "us-east-1",
        "us-east-2",
    ],
    multiselect=True,
    transformer=lambda result: "%s region%s selected"
    % (len(result), "s" if len(result) > 1 else ""),
).execute()
```

</details>

## Keyboard Interrupt

`InquirerPy` will raise exception {class}`KeyboardInterrupt` when `ctrl-c` is pressed by default.

If you prefer to not raise the exception and simply just skip the question, you can do the following:

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

result = prompt({"type": "input", "message": "Name:"}, raise_keyboard_interrupt=False)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

name = inquirer.text(message="Name:").execute(raise_keyboard_interrupt=False)
```

</details>

## Printing Values

```{note}
Printing values while the prompt is running can cause various side effects. Using the patched print function from
`InquirerPy` can print the value above the prompt without causing side effects. Mostly useful for debugging.
```

`InquirerPy` provides a helper function {func}`~InquirerPy.utils.patched_print` which can help printing to the terminal
while the prompt is still running.

```{eval-rst}
.. autofunction:: InquirerPy.utils.patched_print
    :noindex:
```

The following example will print "Hello World" above the prompt when `alt-b` is pressed.

```python
from InquirerPy.utils import patched_print
from InquirerPy import inquirer

prompt = inquirer.text(message="Name:")

@prompt.register_kb("alt-b")
def _(_):
    patched_print("Hello World")

name = prompt.execute()
```

## Color Print

```{note}
This is a standalone feature and will work regardless if the prompt is running or not.
```

`InquirerPy` provides a helper function {func}`~InquirerPy.utils.color_print` which can help print colored messages.

It automatically detects if the current terminal window has a prompt running or not. If the prompt is running, the colored
text will be printed above the running prompt. Otherwise the colored text will simply be outputted to the terminal window.

```{eval-rst}
.. autofunction:: InquirerPy.utils.color_print
    :noindex:
```

![demo](https://assets.kazhala.me/InquirerPy/color_print.gif)

```python
from InquirerPy.utils import color_print
from InquirerPy import inquirer

prompt = inquirer.text(message="Name:")

@prompt.register_kb("alt-b")
def _(_):
    color_print([("#e5c07b", "Hello"), ("#ffffff", "World")])

name = prompt.execute()
color_print([("class:aaa", "fooboo")], style={"aaa": "#000000"})
```
