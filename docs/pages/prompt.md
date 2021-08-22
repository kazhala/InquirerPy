# prompt

This page documents the param and usage of the `prompt` function.
Skip this page if you intend to use the alternate syntax `inquirer`.

`prompt` function resolves user provided list of questions and return the result.

```python
def prompt(
    questions: List[Dict[str, Any]],
    style: Dict[str, str] = None,
    vi_mode: bool = False,
    raise_keyboard_interrupt: bool = True,
    keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
    style_override: bool = False,
) -> Dict[str, Optional[Union[str, List[Any], bool]]]:
```

## Example

![demo](https://github.com/kazhala/gif/blob/master/InquirerPy-prompt.gif)

```python
from InquirerPy import prompt
from InquirerPy.validator import NumberValidator

questions = [
    {
        "type": "input",
        "message": "Enter your age:",
        "validate": NumberValidator(),
        "invalid_message": "Input should be number.",
        "default": "18",
        "name": "age",
        "filter": lambda result: int(result),
        "transformer": lambda result: "Adult" if int(result) >= 18 else "Youth",
    },
    {
        "type": "rawlist",
        "message": "What drinks would you like to buy:",
        "default": 2,
        "choices": lambda result: ["Soda", "Cidr", "Water", "Milk"]
        if result["age"] < 18
        else ["Wine", "Beer"],
        "name": "drink",
    },
    {
        "type": "list",
        "message": "Would you like a bag:",
        "choices": ["Yes", "No"],
        "when": lambda result: result["drink"] in {"Wine", "Beer"},
    },
    {"type": "confirm", "message": "Confirm?", "default": True},
]

result = prompt(questions=questions)
```

## Parameters

### questions: Union[List[Dict[str, Any]], Dict[str, Any]]

A list of questions to ask. If theres only one `question`, you can also just pass in the single `question` dictionary.

#### question

A question object is a Python dictionary consisting of the following keys:

- type: (str) Type of the prompt. Possible values: `input`, `password`, `filepath`, `confirm`
  `list`, `rawlist`, `expand`, `checkbox`, `fuzzy`
- name: (Optional[str]) The key name to use when storing into the result dictionary. If not present,
  the question index within the list of questions will be used as the key name.
- message: (str, Callable[[Dict[str, Any]], str]) The question to print. If passed in as a callable,
  the current prompt result will be passed in as a parameter.
- default: (Union[Any, Callable[[Dict[str, Any]], Any]]) Default value to pass to the prompt. If passed in
  as a callable, the current prompt result will be passed in as a parameter. Checkout individual prompt
  documentation for their available default value.
- validate: (Union[Callable[[Any], bool], Validator]) Check the user answer and return a bool indicating whether the user answer pass the validation or not.
  Reference the [Validator](https://github.com/kazhala/InquirerPy/wiki/Validator) documentation for detailed information.
- invalid_message: (str) The invalid message to display to the user when `validate` failed.
- filter: (Callable[[Any], Any]) Receive the user answer and do post processing before storing the result. The returned
  result will be stored into the prompt result.
- transformer: (Callable[[str], Any]) Receive the user answer and do post processing before displaying the answer in the cli.
  This is only visual effect, use `filter` to affect the actual result. **Note: `filter` function won't affect the answer passed into `transformer`, `transformer` actually run before the `filter` function.**
- when: (Callable[[SessionResult], bool]) Receive the current prompt result and should return a bool determining if
  the question should be asked or skipped.
- qmark: (str) The question mark symbol to display in the prompt. Reference [Style](https://github.com/kazhala/InquirerPy/wiki/Style) documentation
  for detailed information.

Above are the basic keys that are common across all of the prompts. More advanced customization is also available via more key options, reference them in prompt specific documentation.

They are available on the sidebar ⟶ ⟶ ⟶

### style: Dict[str, str]

A dictionary containing the style specification of the prompt. Reference [Style](https://github.com/kazhala/InquirerPy/wiki/Style) documentation for more details.

Default style:

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

### style_override: bool

A boolean to determine if the entire style should be overrided when specifying the `style` parameter.

When `style_override` is `False`, the customized style is merged with the default style:

```python
 before
style = {
    "questionmark": "#000000",
    "answer": "#111111"
    "input": "#222222"
}

 after
style = {
    "questionmark": "#000000",
    "answer": "#111111"
    "input": "#222222"
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

When `style_override` is `True`, the default style is discarded:

```python
 before
style = {
    "questionmark": "#000000",
    "answer": "#111111"
    "input": "#222222"
}

 after
style = {
    "questionmark": "#000000",
    "answer": "#111111"
    "input": "#222222"
}
```

### vi_mode: bool

A boolean to set the keybindings to vi keybindings. This includes the up/down navigation as well as the input editing mode.
This is mainly a shortcut for vim users to enable the vi keybindings without requiring too much customization.

Advanced keybinding customization is documentated [here](https://github.com/kazhala/InquirerPy/wiki/Keybinding).

### raise_keyboard_interrupt: bool

A boolean indicating if the exception `KeyboardInterrupt` should be raised when user hit the sequence of `ctrl-c`.

When set to `False`:

- the exception will not be raised
- result of the current prompt will be `None`
- the question will transition into `skipped` state (UI will reflect based on the style `skipped`)

When set to `True`:

- the exception will be raised
- the prompt will end

### keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]]

Besides the vi_mode keybinding, you can customize the keybindings even further by specifying a dictionary mapping with the pre-defined keybindings.

Reference [Keybinding](https://github.com/kazhala/InquirerPy/wiki/Keybinding) for the detailed explanation.

Default keybindings:

```python
{
    "down": [
        {"key": "down"},
        {"key": "c-n", "filter": ~self._is_vim_edit},
        {"key": "j", "filter": self._is_vim_edit},
    ],
    "up": [
        {"key": "up"},
        {"key": "c-p", "filter": ~self._is_vim_edit},
        {"key": "k", "filter": self._is_vim_edit},
    ],
    "toggle": [
        {"key": "space"},
    ],
    "toggle-down": [
        {"key": Keys.Tab},
    ],
    "toggle-up": [
        {"key": Keys.BackTab},
    ],
    "toggle-all": [
        {"key": "alt-r"},
    ],
    "toggle-all-true": [
        {"key": "alt-a"},
    ],
    "toggle-all-false": [],
}
```
