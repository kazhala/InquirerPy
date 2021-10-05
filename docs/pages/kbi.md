# Keyboard Interrupt

`InquirerPy` will raise exception {class}`KeyboardInterrupt` when `ctrl-c` is pressed by default.

If you prefer to not raise the exception and let `InquirerPy` manage the exception (which simply just skip the question),
you can do the following:

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
