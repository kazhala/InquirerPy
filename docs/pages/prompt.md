# prompt

````{attention}
This document is irrelevant if you intend to use the {ref}`index:Alternate Syntax`.

```{seealso}
{ref}`pages/inquirer:inquirer`
```

````

```{tip}
It's recommended to use {ref}`pages/inquirer:inquirer` over [prompt](#prompt) for new users.
```

This page documents the param and usage of the {func}`~InquirerPy.resolver.prompt` function.
It's the entry point for {ref}`index:Classic Syntax (PyInquirer)`.

## Synchronous execution

```{eval-rst}
.. autofunction:: InquirerPy.resolver.prompt
    :noindex:
```

An example using `prompt` which incorporate multiple different types of prompts:

![demo](https://assets.kazhala.me/InquirerPy/InquirerPy-prompt.gif)

```{eval-rst}
.. literalinclude :: ../../examples/prompt.py
   :language: python
```

### questions

```
Union[List[Dict[str, Any]], Dict[str, Any]]
```

A {class}`list` of question to ask.

```python
from InquirerPy import prompt

questions = [
    {
        "type": "input",
        "message": "Enter your name:",
    },
    {
        "type": "Confirm",
        "message": "Confirm?",
    }
]

result = prompt(questions=questions)
```

If there's only one [question](#question), you can also just provide a {class}`dict` instead of a {class}`list` of {class}`dict`.

```python
from InquirerPy import prompt

result = prompt(questions={"type": "input", "message": "Enter your name:"})
```

#### question

Each question is a Python {class}`dict` consisting the following keys:

```{important}
The list below are the common keys that exists across all types of prompt. Checkout the individual prompt documentation
for their specific options/parameters.
```

- type (`str`): Type of the prompt.

  ```{seealso}
  {ref}`pages/prompts/input:InputPrompt`,
  {ref}`pages/prompts/secret:SecretPrompt`,
  {ref}`pages/prompts/filepath:FilePathPrompt`,
  {ref}`pages/prompts/confirm:ConfirmPrompt`,
  {ref}`pages/prompts/list:ListPrompt`,
  {ref}`pages/prompts/rawlist:RawlistPrompt`,
  {ref}`pages/prompts/expand:ExpandPrompt`,
  {ref}`pages/prompts/checkbox:CheckboxPrompt`,
  {ref}`pages/prompts/fuzzy:FuzzyPrompt`
  ```

- name (`Optional[str]`): The key name to use when storing into the result. If not present, the question index within the list of questions will be used as the key name.
- message (`str, Callable[[Dict[str, Any]], str]`): The question to print. If provided as a function, the current prompt session result will be provided as an argument.
- default (`Union[Any, Callable[[Dict[str, Any]], Any]]`): Default value to set for the prompt. If provided as a function, the current prompt result will be provided as an argument.
  Default values can have different meanings across different types of prompt, checkout individual prompt documentation for more info.
- validate (`Union[Callable[[Any], bool], Validator]`): Check the user answer and return a {class}`bool` indicating whether the user answer passes the validation or not.
  ```{seealso}
  {ref}`pages/validator:Validator`
  ```
- invalid_message (`str`): The invalid message to display to the user when `validate` failed.
  ```{seealso}
  {ref}`pages/validator:Validator`
  ```
- filter (`Callable[[Any], Any]`): A function which performs additional transformation on the result. This affects the actual value stored in the final result.
- transformer (`Callable[[str], Any]`): A function which performs additional transformation on the value that gets printed to the terminal. Different than the `filter` key, this
  is only visual effect and won't affect the final result.

  ```{tip}
  `filter` and `transformer` key run separately and won't have side effects when running both.
  ```

- when (`Callable[[SessionResult], bool]`): A function to determine if the question should be asked or skipped. The current prompt session result will be provided as an argument.
  You can use this key to ask certain questions based on previous question answer conditionally.
- qmark (`str`): Custom symbol that will be displayed in front of the question message before its answered.
- amark (`str`): Custom symbol that will be displayed in front of the question message after its answered.
- instruction (`str`): Short instruction to display next to the question message.
- wrap_lines (`bool`): Soft wrap question line when question message exceeds the terminal width.
- mandatory (`bool`): Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
- mandatory_message (`str`): Error message to show when user attempts to skip mandatory prompt.
- raise_keyboard_interrupt (`bool`): Raise the {class}`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
  will be `None` and the question is skipped.

## Asynchronous execution

```{eval-rst}
.. autofunction:: InquirerPy.resolver.prompt_async
    :noindex:
```

```{code-block} python
import asyncio

from InquirerPy import inquirer, prompt_async


async def main():
    questions = [
        {"type": "input", "message": "Name:"},
        {"type": "number", "message": "Number:"},
        {"type": "confirm", "message": "Confirm?"},
    ]
    result = await prompt_async(questions)


if __name__ == "__main__":
    asyncio.run(main())
```
