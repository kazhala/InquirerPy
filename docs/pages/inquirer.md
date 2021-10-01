# inquirer

````{attention}
This document is irrelevant if you intend to use the {ref}`index:Classic Syntax (PyInquirer)`.

```{seealso}
{ref}`pages/prompt:prompt`
```

````

This page documents the usage of `inquirer`.

```{eval-rst}
.. automodule:: InquirerPy.inquirer
    :noindex:
```

An example using `inquirer` which incorporate multiple different types of prompts:

![demo](https://assets.kazhala.me/InquirerPy/InquirerPy-prompt.gif)

```{eval-rst}
.. literalinclude :: ../../examples/example_inquirer.py
   :language: python
```

## Usage

```{note}
The `inquirer` module serves as an entry point to each prompt classes. Refer to
individual prompt documentation for prompt specific usage.
```

```{include} ./prompt.md
:start-after: <!-- start raise -->
:end-before: <!-- end raise -->
```

```python
from InquirerPy import inquirer

result = inquirer.text(message="Name:").execute(raise_keyboard_interrupt=False)
```

```{include} ./prompt.md
:start-after: <!-- start raise continue -->
:end-before: <!-- end raise continue -->
```
