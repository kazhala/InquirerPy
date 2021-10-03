# ExpandPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.expand.ExpandPrompt
    :noindex:
```

## Example

![demo](https://assets.kazhala.me/InquirerPy/expand.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/expand.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/expand.py
   :language: python
```

</details>

## Choices

```{seealso}
{ref}`pages/dynamic:choices`
```

```{attention}
Each choice for {ref}`pages/prompts/expand:ExpandPrompt` is required to be either an instance {class}`dict` or {ref}`pages/separator:Separator`.
```

```{tip}
Do not specify the `h` key, since its already taken and used as the expand key. Also avoid specifying keys such as `j`
and `k` as they are used for navigation for `vi_mode`.
```

For this specific prompt, in addition to the 2 required keys `name` and `value`, the `key` is also required.
The `key` is the char to bind to the choice. On prompt creation, a keybinding will be created for the char and then
pressing the char can jump to the choice.

```{code-block}
choices = [
    {"key": "a", "name": "Apple", "value": "Apple"},
    {"key": "c", "name": "Cherry", "value": "Cherry"},
    {"key": "o", "name": "Orange", "value": "Orange"},
    {"key": "p", "name": "Peach", "value": "Peach"},
    {"key": "m", "name": "Melon", "value": "Melon"},
    {"key": "s", "name": "Strawberry", "value": "Strawberry"},
    {"key": "g", "name": "Grapes", "value": "Grapes"},
]
```

## Keybindings

```{seealso}
{ref}`pages/prompts/list:keybindings`
```

In addition to the keybindings mentioned {ref}`here <pages/prompts/list:keybindings>`, keybindings are created for all the
`key` specified for each choice which you can use to jump the target choice.

## Multiple Selection

```{seealso}
{ref}`pages/prompts/list:Multiple Selection`
```

## Default Value

The `default` parameter for expand prompt can be two types of values:

- shortcut char (str): one of the `key` assigned to the choice.
- choice["value"] (Any): default value could be the value key for one of the choice.
