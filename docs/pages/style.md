# Style

Each `InquirerPy` prompt contains several [components](#components) which you can
[customize](#customizing-style) the style.

## Customizing Style

### `get_style`

````{note}
```{eval-rst}
Skip this section if you are using :ref:`index:Classic Syntax (PyInquirer)`.
```

````

```{eval-rst}
When using the :ref:`index:Alternate Syntax`, each `prompt` class requires a :class:`~InquirerPy.utils.InquirerPyStyle` instance instead of a dictionary. You can get
this object by using :func:`~InquirerPy.utils.get_style`.

.. autofunction:: InquirerPy.utils.get_style
  :noindex:
```

### Default Style

```{note}
The default style is based on [onedark](https://github.com/joshdick/onedark.vim/blob/master/colors/onedark.vim) color palette.
```

Checkout [Components](#components) to see how the following styles are applied to each `prompt`.

```python
{
    "questionmark": "#e5c07b",
    "answermark": "#e5c07b",
    "answer": "#61afef",
    "input": "#98c379",
    "question": "",
    "answered_question": "",
    "instruction": "#abb2bf",
    "pointer": "#61afef",
    "checkbox": "#98c379",
    "separator": "",
    "skipped": "#5c6370",
    "validator": "",
    "marker": "#e5c07b",
    "fuzzy_prompt": "#c678dd",
    "fuzzy_info": "#abb2bf",
    "fuzzy_border": "#4b5263",
    "fuzzy_match": "#c678dd",
    "spinner_pattern": "#e5c07b",
    "spinner_text": "",
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

- [ANSI color palette](https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#8-colors): `ansired`
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

The styling functionality leverages [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit).
For more reference of the styling options, visit `prompt_toolkit` [documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/styling.html).

The colors and styling support will be limited by the terminal and font and experience may vary between different environments. Avoid
adding styles such as `italic` since lots of font or terminal doesn't support it.

## Components

![style1](https://assets.kazhala.me/InquirerPy/inquirerpy-style1.png)
![style2](https://assets.kazhala.me/InquirerPy/inquirerpy-style2.png)
![style3](https://assets.kazhala.me/InquirerPy/inquirerpy-style3.png)
