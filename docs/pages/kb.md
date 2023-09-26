# Keybindings

By default, `InquirerPy` will use most of the standard `emacs` navigation keybindings. You
can easily switch to `vim` keybindings by setting the parameter [vi_mode](#using-vim-keybindings) to `True`.

You can customise the keybindings even further by utilising the parameter [keybindings](#customizing-keybindings).

## Default Keybindings

```{note}
Each keybinding consists of 2 parts, an **action** as the key and **bindings** as the value.
```

The following dictionary contains the default keybindings for all prompts.

<!-- start kb -->

```{code-block} python
{
    "answer": [{"key": "enter"}],   # answer the prompt
    "interrupt": [{"key": "c-c"}],  # raise KeyboardInterrupt
    "skip": [{"key": "c-z"}],   # skip the prompt
}
```

<!-- end kb -->

### Input Buffer (Text Fields)

The default keybinding for text fields uses the classic `emacs` keybindings.

You can use the regular `emacs` shortcuts to move between words such as `alt-b` and `alt-f` in any input buffer
such as `input`, `secret`, `filepath` and `fuzzy`.

You can reference keybindings through `emacs` [documentation](https://www.gnu.org/software/emacs/refcards/).

### Prompt Specific Keybindings

```{tip}
Keybindings in different types of prompt can have different sets of available actions and sometimes different default bindings.

Please checkout the individual prompt documentation for the available actions and default bindings for specific prompts.
```

## Using VIM Keybindings

```{tip}
All `InquirerPy` prompts accepts a boolean parameter `vi_mode`.
```

`InquirerPy` comes with `vim` keybinding preset. After setting `vi_mode=True`, the input buffer (text fields) will behave the same as
if you enable the `vi` mode in [readline/bash](https://www.gnu.org/software/bash/manual/html_node/Readline-vi-Mode.html).
Other keybinding will also have different effects (e.g. `up/down` will change from `ctrl-n/ctrl-p` to `j/k`), refer to individual
prompt documentation for more information.

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
        },
    ],
    vi_mode=True,
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    vi_mode=True,
).execute()
```

</details>

## Customising Keybindings

### keybindings

```
Dict[str, List[Dict[str, Union[str, "FilterOrBool", List[str]]]]]
```

`keybindings` should be a {class}`dict` where the `key` is the **action** and the `value` should be a list of keys that
will be the **bindings** to trigger it.

```{admonition} action
You can find the available actions via individual prompt documentation.
```

```{admonition} bindings
Each `binding` is another {class}`dict` which contains the following key:

- [key](#key-union-str-list-str)
- [filter](#filter-union-filter-bool)
```

#### key

The `key` can be either a list or a string. If you require multiple keys to be pressed in sequence, provide the `key` with a list of keys.

In the following example:

- pressing `ctrl-a` followed by `space` will trigger the action `toggle-all`
- pressing `ctrl-d` will raise {class}`KeyboardInterrupt`
- pressing `ctrl-c` will attempt to skip the prompt

<details>
  <summary>Classic Syntax</summary>

```python
from InquirerPy import prompt

keybindings = {
    "skip": [{"key": "c-c"}],
    "interrupt": [{"key": "c-d"}],
    "toggle-all": [{"key": ["c-a", "space"]}],
}

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
            "multiselect": True
        },
    ],
    keybindings=keybindings,
)
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```python
from InquirerPy import inquirer

keybindings = {
    "skip": [{"key": "c-c"}],
    "interrupt": [{"key": "c-d"}],
    "toggle-all": [{"key": ["c-a", "space"]}],
}

result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    keybindings=keybindings,
    multiselect=True
).execute()
```

</details>

Available keys/syntax:

| Name               | Possible keys                                           |
| ------------------ | ------------------------------------------------------- |
| Escape             | `escape`                                                |
| Arrows             | `left`, `right`, `up`, `down`                           |
| Navigation         | `home`, `end`, `delete`, `pageup`, `pagedown`, `insert` |
| Control+lowercase  | `c-a`, `c-b` ... `c-y`, `c-z`                           |
| Control+uppercase  | `c-A`, `c-B` ... `c-Y`, `c-Z`                           |
| Control + arrow    | `c-left`, `c-right`, `c-up`, `c-down`                   |
| Other control keys | `c-@`, `c-\`, `c-]`, `c-^`, `c-\_`, `c-delete`          |
| Shift + arrow      | s-left, s-right, s-up, s-down                           |
| Other shift keys   | `s-delete`, `s-tab`                                     |
| F-keys             | `f1`, `f2`, .... `f23`, `f24`                           |
| Alt+lowercase      | `alt-a`, `alt-b` ... `alt-y`, `alt-z`                   |
| Alt+uppercase      | `alt-A`, `alt-B` ... `alt-Y`, `alt-Z`                   |

Visit `prompt_toolkit` [documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html#list-of-special-keys)
for more information about limitations and other advanced topics.

#### filter

Each keybinding also takes another **optional** key called `filter` which can be used to determine if certain keys should be enabled/disabled.
The `filter` key can be either a boolean or a `prompt_toolkit` [Condition](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/filters.html#filters).

**bool**

```python
special_vim = True

keybindings = {
    "down": [
        {"key": "c-j", "filter": special_vim},
    ],
    "up": [
        {"key": "c-k", "filter": special_vim},
    ],
    "toggle-all-false": [{"key": "alt-x"}],
}

# ....
```

**Filter**

```python
from prompt_toolkit.filters.base import Condition

@Condition
def special_vim():
    # logic ...
    return True

keybindings = {
    "down": [
        {"key": "c-j", "filter": special_vim},
    ],
    "up": [
        {"key": "c-k", "filter": special_vim},
    ],
    "toggle-all-false": [{"key": "alt-x"}],
}

# ....
```

## Binding Custom Functions

```{attention}
This section only applies to {ref}`index:Alternate Syntax`.
```

You can also create your own keybindings/actions. When creating a prompt via `inquirer`, instead of running
the `execute` function immediately, you can bind keys to your custom functions before running `execute` on the prompt.

### register_kb

```{seealso}
This method directly interacts with {meth}`prompt_toolkit.key_binding.KeyBindings.add`.
```

{meth}`~InquirerPy.base.simple.BaseSimplePrompt.register_kb` is a decorator function that's available to use once the prompt is created.
The function that are being bounded will be provided with an object {class}`~prompt_toolkit.key_binding.key_processor.KeyPressEvent` as an argument.

The {class}`~prompt_toolkit.key_binding.key_processor.KeyPressEvent` can give you access to the {class}`~prompt_toolkit.application.Application` which
will provide you with the ability to exit the prompt application with custom result.

```{code-block} python
from InquirerPy import inquirer

prompt = inquirer.select(
    message="Select item:",
    choices=["foo", "bar"],
    long_instruction="ENTER=view, D=delete",
)

@prompt.register_kb("d")
def _handle_delete(event):
    choice_name = prompt.result_name
    choice_value= prompt.result_value
    # some logic for processing
    # ...
    # you can then use the event API to exit the prompt with the value you desired
    event.app.exit(result=None)

result = prompt.execute()
```

There are also some internal APIs you could leverage within the keybinding functions.

```{code-block} python
from InquirerPy import inquirer

prompt = inquirer.select(
    message="Select item:",
    choices=["foo", "bar"],
    long_instruction="ENTER=view, D=delete",
)

@prompt.register_kb("d")
def _handle_delete(event):
    choice_name = prompt.result_name
    choice_value= prompt.result_value
    # some logic for processing
    # ...
    # skipping the prompt after processing
    prompt._mandatory = False
    prompt._handle_skip(event)
    # answer the prompt normally after processing
    prompt._handle_enter(event)

result = prompt.execute()
```

The following is a simpler example which will print "Hello World" on top of the prompt when pressing `alt-a`.

```{code-block} python
from InquirerPy import inquirer
from InquirerPy.utils import patched_print as print

name_prompt = inquirer.text(message="Name:")

kb_activate = True

@name_prompt.register_kb("alt-a")
def _(_):
    print("Hello World")

name = name_prompt.execute()
```

**keys and filter**

You can bind multiple keys and also have the ability to apply [filter](#filter).

```python
from prompt_toolkit.filters.base import Condition

hello_active = Condition(lambda: True)
world_active = False

@name_prompt.register_kb("alt-j", "alt-k" filter=hello_active)
def _(_):
    print("Hello")

@name_prompt.register_kb("escape", "k", "escape", "j" filter=world_active)
def _(_):
    print("World")
```
