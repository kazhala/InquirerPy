# Environment Variables

```{tip}
If you make calls to `InquirerPy` multiple times with a lot of customisation, you can consider utilising ENV variables.
```

Several options can be configured via ENV variables.

## Style

```{note}
Checkout {ref}`pages/style:Style` for more information about style customisation.
```

```{admonition} Priority
ENV -> `style` parameter -> default style
```

### Usage

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt
from InquirerPy import get_style

# before
result = prompt(questions=[{"type": "confirm", "message": "Confirm?"}], style={"questionmark": "#ffffff"})

# after
import os
os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = "#ffffff"
result = prompt(questions=[{"type": "confirm", "message": "Confirm?"}])
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer
from InquirerPy import get_style

# before
result = inquirer.confirm(message="Confirm?", style=get_style({"questionmark": "#ffffff"})).execute()

# after
import os
os.environ["INQUIRERPY_STYLE_QUESTIONMARK"] = "#ffffff"
result = inquirer.confirm(message="Confirm?").execute()
```

</details>

### Mapping

| style class       | ENV                                |
| ----------------- | ---------------------------------- |
| questionmark      | INQUIRERPY_STYLE_QUESTIONMARK      |
| answermark        | INQUIRERPY_STYLE_ANSWERMARK        |
| answer            | INQUIRERPY_STYLE_ANSWER            |
| input             | INQUIRERPY_STYLE_INPUT             |
| question          | INQUIRERPY_STYLE_QUESTION          |
| answered_question | INQUIRERPY_STYLE_ANSWERED_QUESTION |
| instruction       | INQUIRERPY_STYLE_INSTRUCTION       |
| pointer           | INQUIRERPY_STYLE_POINTER           |
| checkbox          | INQUIRERPY_STYLE_CHECKBOX          |
| separator         | INQUIRERPY_STYLE_SEPARATOR         |
| skipped           | INQUIRERPY_STYLE_SKIPPED           |
| validator         | INQUIRERPY_STYLE_VALIDATOR         |
| marker            | INQUIRERPY_STYLE_MARKER            |
| fuzzy_prompt      | INQUIRERPY_STYLE_FUZZY_PROMPT      |
| fuzzy_info        | INQUIRERPY_STYLE_FUZZY_INFO        |
| fuzzy_border      | INQUIRERPY_STYLE_FUZZY_BORDER      |
| fuzzy_match       | INQUIRERPY_STYLE_FUZZY_MATCH       |
| spinner_pattern   | INQUIRERPY_STYLE_SPINNER_PATTERN   |
| spinner_text      | INQUIRERPY_STYLE_SPINNER_TEXT      |

## Keybinding

```{note}
Checkout {ref}`pages/kb:Keybindings` for more information about customising keybindings.
```

```{admonition} Priority
ENV -> `vi_mode` parameter
```

### Usage

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

# before
result = prompt(questions=[{"type": "input", "message": "Name:"}], vi_mode=True)

# after
import os
os.environ["INQUIRERPY_VI_MODE"] = "true"
result = prompt(questions=[{"type": "input", "message": "Name:"}])
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

# before
result = inquirer.text(message="Name:", vi_mode=True).execute()

# after
import os
os.environ["INQUIRERPY_VI_MODE"] = "true"
result = inquirer.text(message="Name").execute()
```

</details>

### Mapping

```{note}
The value of `INQUIRERPY_VI_MODE` does not matter, as long as its a string longer than 0, `InquirerPy` will set `vi_mode=True`.
```

| parameter      | ENV                |
| -------------- | ------------------ |
| `vi_mode=True` | INQUIRERPY_VI_MODE |

## Keyboard Interrupt

```{note}
Classic Syntax: Checkout {ref}`pages/prompt:Keyboard Interrupt` section for more information.
Alternate Syntax: Checkout {ref}`pages/inquirer:Keyboard Interrupt` section for more information.
```

```{admonition} Priority
ENV -> `raise_keyboard_interrupt` parameter
```

### Usage

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

# before
result = prompt(questions=[{"type": "secret", "message": "Password:"}], raise_keyboard_interrupt=False)

# after
import os
os.environ["INQUIRERPY_NO_RAISE_KBI"] = "true"
result = prompt(questions=[{"type": "secret", "message": "Password:"}])
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

# before
result = inquirer.text(message="Name:", vi_mode=True).execute(raise_keyboard_interrupt=False)

# after
import os
os.environ["INQUIRERPY_NO_RAISE_KBI"] = "true"
result = inquirer.text(message="Name").execute()
```

</details>

### Mapping

```{note}
The value of `INQUIRERPY_NO_RAISE_KBI` does not matter, as long as its a string longer than 0,
InquirerPy will not raise {class}`KeyboardInterrupt` when user hit `ctrl-c`.
```

| parameter                        | ENV                     |
| -------------------------------- | ----------------------- |
| `raise_keyboard_interrupt=False` | INQUIRERPY_NO_RAISE_KBI |
