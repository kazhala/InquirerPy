# Keybindings

One of the issues `PyInquirer` was facing is the lack of keybinding customization,
especially the highly requested `vim` navigation. `InquirerPy` offers a parameter
`vi_mode` which will automatically apply `vim` keybindings to input buffer as well
as list type prompts navigations.

`InquirerPy` takes the keybindings customization to another level where you can also
customize any supported keybindings with your own keys and filter.

## Default Keybindings

The default keybindings is a classic `emacs` keybindings.

> This is done because on most operating systems, also the Bash shell uses Emacs bindings by default, and that is more intuitive. If however, Vi binding are required, just pass vi_mode=True

### Input Buffer

You can use the regular `emacs` cursor shortcuts to move between words such as `alt-b` and `alt-f` in any input buffer
such as `input`, `secret`, `filepath` and `fuzzy`.

You can reference keybindings through `emacs` [documentation](http://ergoemacs.org/emacs/emacs_keys_basics.html).

### Available Actions and Keybindings

The following dictionary contains the default keybindings that applies to all list type prompts. Only
`down` and `up` will be active at all time, other actions are only active when the list type prompt is
`multiselect` prompt or `checkbox`.

```python
{
    "down": [
        {"key": "down"},
        {"key": "c-n"},  # ctrl-n
    ],
    "up": [
        {"key": "up"},
        {"key": "c-p"}, # ctrl-p
    ],
    "toggle": [
        {"key": "space"},
    ],
    "toggle-down": [
        {"key": "c-i"}, # tab
    ],
    "toggle-up": [
        {"key": "s-tab"}, # shift + tab
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

## `vi_mode`

All `InquirerPy` prompts accepts a boolean parameter `vi_mode` which will set both the keybinding of input buffer and
list navigation to `vim` keybindings.

```python
from InquirerPy import prompt
from InquirerPy import inquirer

result = prompt(
    questions=[
        {"type": "input", "message": "Name:"},
        {"type": "input", "message": "Address:"},
    ],
    vi_mode=True,
)
result = inquirer.text(message="Name:", vi_mode=True)
```

The input buffer will behave the same as if you enable the `vi` mode in [readline/bash](https://www.gnu.org/software/bash/manual/html_node/Readline-vi-Mode.html). The
navigation `up` and `down` will replace the `emacs` keybindings to `vim`.

```python
{
    "down": [
        {"key": "down"},
        {"key": "j"}, # ctrl-n is removed
    ],
    "up": [
        {"key": "up"},
        {"key": "k"}, # ctrl-p is removed
    ],
    # ....
}
```

## Customizing Keybindings

All the actions/keybinding in the [Available actions and keybindings](#available-actions-and-keybindings) are customizable. Each `InquirerPy` prompt
takes an additional parameter called `keybindings`.

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

### keybindings: Dict[str, List[Dict[str, Any]]]

The provided `keybindings` will be merged with the default `keybindings`, the structure of this dictionary is exactly the same as the dictionary
in the [Available actions and keybindings](#available-actions-and-keybindings) section.

The `key` can be either a list or a string. If you require multiple keys to be pressed in sequence, provide the `key` with a list of keys.
The following example maps the action `toggle-all` to press `c-a` and then press `space`.

```python
keybindings = {
    "toggle": [
        {"key": "space"}
    ],
    "toggle-all": [
        {"key": ["c-a", "space"]}
    ]
}
```

The following example enabled `vim` keybindings for input buffer, but still uses `c-n` and `c-p` for list navigations. It also enabled
the shortcut `alt-x` to deselect all choices/checkbox.

```python
from InquirerPy import prompt
from InquirerPy import inquirer

keybindings = {
    "down": [
        {"key": "c-n"},
    ],
    "up": [
        {"key": "c-p"},
    ],
    "toggle-all-false": [{"key": "alt-x"}],
}

result = prompt(
    questions=[
        {
            "type": "list",
            "message": "Select one:",
            "choices": ["Fruit", "Meat", "Drinks", "Vegetable"],
        },
    ],
    vi_mode=True,
    keybindings=keybindings,
)
result = inquirer.select(
    message="Select one:",
    choices=["Fruit", "Meat", "Drinks", "Vegetable"],
    vi_mode=True,
    keybindings=keybindings,
)
```

#### filter: Union[Filter, bool]

Each keybinding also takes another key called `filter` which can be used to determine if certain keys should be enabled/disabled.
The `filter` key can be either a boolean or a `prompt_toolkit` [Conditon](https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/filters.html#filters).

##### bool

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

##### Filter

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

> This is only available for `Alternate Syntax` (i.e. using `inquirer`).

You can also create your own keybindings/actions. When creating a prompt via `inquirer`, instead of running
the `execute` function immediately, you can bind keys to your custom functions before running the prompt.

### `register_kb`

`register_kb` is a decorator function thats available to use once the prompt is created.
The function that are being binded will be provided by a parameter `event`. The `event` can give
you access to the `application` (`event.app`). It's more of a `prompt_toolkit`
, if you don't plan to use it, simply provide a dummy parameter `_`.

The following example will print "Hello World" on top of the prompt when pressing `alt-a`.

```python
from InquirerPy import inquirer
from InquirerPy.utils import patched_print as print

name_prompt = inquirer.text(message="Name:")

kb_activate = True

@name_prompt.register_kb("alt-a")
def _(_):
    print("Hello World")

name = name_prompt.execute()
```

#### keys and filter

You can bind multiple keys and also have the ability to apply [filter](#filter-unionfilter-bool).

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
