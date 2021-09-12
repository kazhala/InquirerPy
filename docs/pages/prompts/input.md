# InputPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.input.InputPrompt
    :noindex:
```

## Auto Completion

You can add auto completion to the prompt via the parameter/key `completer`. Provide a Completer class or a dictionary of words to enable auto-completion of the prompt.
Use ctrl-space to force auto-completion popup. Below is a simple word dictionary completer.

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
