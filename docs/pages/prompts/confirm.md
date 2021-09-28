# ConfirmPrompt

```{eval-rst}
.. automodule:: InquirerPy.prompts.confirm
    :members:
```

## Example

![demo](https://assets.kazhala.me/InquirerPy/confirm.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/confirm.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/confirm.py
   :language: python
```

</details>

## Using Different Letters For Confirm/Deny

In certain scenarios using `Y/y` for "yes" and `N/n` for "no" may not
be appropriate (e.g. multilingual).

You can change this behavior by customising the following parameters:

- `confirm_letter`
- `reject_letter`
- `transformer`

```{hint}
Changing the `transformer` is also necessary as the default behavior will print `Yes` for `True`
value and `No` for `False` value.
```

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{code-block} python
from InquirerPy import prompt

questions = [
  {
    "type": "confirm",
    "default": True,
    "message": "Proceed?",
    "confirm_letter": "s",
    "reject_letter": "n",
    "transformer": lambda result: "SIm" if result else "Não",
  }
]

result = prompt(questions=questions)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{code-block} python
from InquirerPy import inquirer

inquirer.confirm(
    message="Proceed?",
    default=True,
    confirm_letter="s",
    reject_letter="n",
    transformer=lambda result: "SIm" if result else "Não",
).execute()
```

</details>
