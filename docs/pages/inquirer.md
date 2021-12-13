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
.. literalinclude :: ../../examples/inquirer.py
   :language: python
```

```{important}
The `inquirer` module serves as an entry point to each prompt classes. Refer to
individual prompt documentation for prompt specific usage.
```

## Synchronous execution

Each prompt contains a function `execute` to start the prompt.

```{code-block} python
from InquirerPy import inquirer

def main():
  result = inquirer.text(message="Name:").execute()

if __name__ == "__main__":
  main()
```

## Asynchronous execution

Each prompt contains a function `execute_async` to start the prompt asynchronously.

```{code-block} python
import asyncio
from InquirerPy import inquirer

async def main():
  result = await inquirer.text(message="Name:").execute_async()

if __name__ == "__main__":
  asyncio.run(main())
```
