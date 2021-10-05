# InputPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.input.InputPrompt
    :noindex:
```

## Example

![demo](https://assets.kazhala.me/InquirerPy/InquirerPy-input.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/input.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/input.py
   :language: python
```

</details>

## Keybindings

```{seealso}
{ref}`pages/kb:Default Keybindings`

{ref}`pages/kb:Input Buffer (Text Fields)`
```

Besides the default keybindings and input buffer keybindings, if you have autocompletion enabled, you can use
`ctrl-space` to trigger completion window popup.

## Auto Completion

```{tip}
Use `ctrl-space` to force completion window popup.
```

You can add auto completion to the prompt via the parameter/key `completer`. Provide a {class}`~prompt_toolkit.completion.Completer` class or a dictionary of words to enable auto-completion of the prompt.
Below is a simple {class}`dict` completer.

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

completer = {
    "hello": {
        "world": None
    },
    "foo": {
        "boo": None
    },
    "fizz": {
        "bazz": None
    }
}

questions = [
    {
        "type": "input",
        "message": "FooBoo:",
        "completer": completer
    }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

completer = {
    "hello": {
        "world": None
    },
    "foo": {
        "boo": None
    },
    "fizz": {
        "bazz": None
    }
}

result = inquirer.text(message="FooBoo:", completer=completer).execute()
```

</details>

Checkout `prompt_toolkit` [documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#autocompletion)
for more examples and information on how to create more dynamic/complex completer.

## Multi-line Input

By setting the parameter `multiline` to `True`, the prompt will change from single line input to multiple line input.
While `multiline` is `True`, `enter` will causing a new line to be used instead of finish answering the question. Press
`esc` and then press `enter` to finish answer the question.

```{code-block} python
from InquirerPy import inquirer

result = inquirer.text(message="FooBoo:", multiline=True).execute()
```
