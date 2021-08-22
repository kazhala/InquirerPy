# Style

This page documents the guide to customize the style of the prompt.

## Components

![style1](https://assets.kazhala.me/InquirerPy/inquirerpy-style1.png)
![style2](https://assets.kazhala.me/InquirerPy/inquirerpy-style2.png)
![style3](https://assets.kazhala.me/InquirerPy/inquirerpy-style3.png)

### Before Answered

All prompts contains at least one window with the following components. These can be supplied
to the prompt via parameters.

```
    ? What's your name: (full name) Kevin█
    - ----------------- ----------- -----
    ↑      ↑                ↑         ↑
    ↑      ↑                ↑         ↑
  qmark message         instruction  input

    ? Select prefered methods: (j/k)
     >Pick-up
    >>Delivery
      ---------      ← separator
      Drive-through
    ↑↑
    ↑↑
pointer & marker
```

### After Answered

```
    ? What's your name: Kevin Zhuang
    ? Select prefered methods: ["Pick-up", "Delivery"]
    - ------------------------ -----------------------
    ↑      ↑                               ↑
    ↑      ↑                               ↑
  qmark message                          answer
```

### Style - Components Mapping

The following table contains the mapping between configurable components and their style class.

You will find these components as a parameter in individual prompt documentation →→→

| Style class    | Components                         |
| -------------- | ---------------------------------- |
| `questionmark` | `qmark`                            |
| `question`     | `message`                          |
| `instruction`  | `instruction`                      |
| `pointer`      | `pointer`                          |
| `checkbox`     | `enabled_symbol`/`disabled_symbol` |
| `marker`       | `marker`                           |

## Customizing Style

### `get_style`

> Skip this section if you are coming from `PyInquirer` / using the "classic syntax" (i.e. using the `prompt` module)

When using the "alternate syntax" (i.e. interacting with the `inquirer` module), each prompt class requires a `InquirerPyStyle` object instead of a dictionary. You can get
this object by using the `get_style` method.

```python
def get_style(
    style: Dict[str, str] = None, style_override: bool = True
) -> InquirerPyStyle:
```

```python
from InquirerPy import get_style
from InquirerPy import inquirer

style = get_style({"questionmark": "#ffffff", "answer": "#000000"})
result = inquirer.confirm(message="Confirm?", style=style)
```

#### Parameters

##### style: Dict[str, str]

The dictionary of style classes and their colors, reference [Default Style](#default-style). If nothing is passed, the style will be resolved
to the default style.

##### style_override: bool

A boolean to determine if the supplied `style` parameter should be merged with the default style or override the entire default style.

By default, the supplied style will overwrite the entire default style.

Set to `False` if you like the default onedark style or just playing around the styling options to have the supplied `style` merge with the default `style`.

### Default Style

The default style is based on onedark color scheme ([reference](https://github.com/joshdick/onedark.vim/blob/master/colors/onedark.vim)).

```python
{
    "questionmark": "#e5c07b",
    "answer": "#61afef",
    "input": "#98c379",
    "question": "",
    "instruction": "",
    "pointer": "#61afef",
    "checkbox": "#98c379",
    "separator": "",
    "skipped": "#5c6370",
    "validator": "",
    "marker": "#e5c07b",
    "fuzzy_prompt": "#c678dd",
    "fuzzy_info": "#98c379",
    "fuzzy_border": "#4b5263",
    "fuzzy_match": "#c678dd",
}
```

### Color Syntax

Applying basic style.

```python
{
    "questionmark": "blue"
}
```

Coloring both foreground and background.

```python
{
    "questionmark": "fg:#e5c07b bg:#ffffff"
}
```

Adding additional styles to text.

```python
{
    "questionmark": "fg:#e5c07b bg:#ffffff underline bold"
}
```

### Available Options

#### Colors

- ANSI color palette: `ansired`
- Named color: `red`
- Hexadecimal notation: `#ffffff`

#### Text

- `underline`
- `italic`
- `bold`
- `reverse`
- `hidden`
- `blink`

##### Negative Variants

- `noblink`
- `nobold`
- `nounderline`
- `noreverse`
- `nohidden`
- `noitalic`

### Support

The styling functionality leverages `prompt_toolkit`. For more reference of the styling options, visit `prompt_toolkit` [documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/styling.html).

The colors and styling support will be limited by the terminal and font and experince may vary. Avoid
adding styles such as `italic` since lots of font or terminal doesn't support it.
