# filepath

A text prompt which provides auto completion for system paths.

## Example

![demo](https://assets.kazhala.me/InquirerPy/filepath.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/classic/filepath.py
   :language: python
```

</details>

<details open>
  <summary>Alternate Syntax</summary>

```{eval-rst}
.. literalinclude :: ../../../examples/alternate/filepath.py
   :language: python
```

</details>

## Keybindings

```{seealso}
{ref}`pages/kb:Keybindings`
```

```{include} ../kb.md
:start-after: <!-- start kb -->
:end-before: <!-- end kb -->
```

In addition the default keybindings, you can use `ctrl-space` to trigger completion window popup.

```
{
    "completion": [{"key": "c-space"}]  # force completion popup
}
```

## Symbols and ENV Variables

The auto completion can handle `~` and will start triggering completion for the home directory. However it does not handle ENV variable
such as `$HOME`.

If you wish to support ENV variables completion, look into `prompt_toolkit` [documentation](https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#autocompletion)
and create a custom completion class. Directly use the {ref}`pages/prompts/input:InputPrompt` with the parameter `completer`.

```{seealso}
{class}`InquirerPy.prompts.filepath.FilePathCompleter`
```

## Excluding File Types

This class contains 2 basic variables `only_directories` and `only_files` that can control whether to only list
files or directories in the completion.

```{note}
`only_directories` takes higher priority over `only_files`.
```

```{seealso}
[Example](#example)
```

## Reference

```{eval-rst}
.. autoclass:: InquirerPy.prompts.filepath.FilePathPrompt
    :noindex:
```
