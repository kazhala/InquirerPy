# RawlistPrompt

```{eval-rst}
.. autoclass:: InquirerPy.prompts.rawlist.RawlistPrompt
    :noindex:
```

## Example

![demo](https://assets.kazhala.me/InquirerPy/rawlist.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/rawlist.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/rawlist.py
   :language: python
```

</details>

## Choices

```{seealso}
{ref}`pages/dynamic:choices`
```

For this specific prompt, due to the shortcut being created is between 1-9, the total length of choices cannot exceed 10.

## Keybindings

```{seealso}
{ref}`pages/prompts/list:keybindings`
```

In addition to the keybindings mentioned {ref}`here <pages/prompts/list:keybindings>`, keybindings are created for keys 1-9
to jump to the target index choices.

## Multiple Selection

```{seealso}
{ref}`pages/prompts/list:Multiple Selection`
```

## Default Value

```{seealso}
{ref}`pages/prompts/list:Default Value`
```

The `default` parameter for rawlist can be three types of values:

- shortcut index (int): an {class}`int` value between 1-9 and the default value index choice will be highlighted.
- choice value (Any): default value could the value of one of the choices.
