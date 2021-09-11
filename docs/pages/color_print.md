# `color_print`

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
