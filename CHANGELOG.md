# CHANGELOG

Notable changes are documented in this file.

## Dev

### Added

- Added option `wrap_lines` to all prompts to configure line wrapping
- Added option `instruction` for non-list type prompts. This is already supported in all list type prompts previously.

### Fixed

- Line wrapping [#11](https://github.com/kazhala/InquirerPy/issues/11)

## 0.2.2 (03/07/2021)

N/A

## 0.2.1 (03/07/2021)

### Added

- Added option to disable cycle behavior in list type prompts [#9](https://github.com/kazhala/InquirerPy/issues/9)
- Added parameter `amark`. You can use this value to change the `qmark` after the question is answered.
- Added some more style customization option.
  - `answermark`: Used to change the color and style of `amark`.
  - `answered_question`: Used to change the color and style of `question` message once the question is answered.

## 0.2.0 (01/05/2021)

### Added

- Defaults for multi-select list [#2](https://github.com/kazhala/InquirerPy/issues/2)
- Disable qmark [#3](https://github.com/kazhala/InquirerPy/issues/3)
- Configure `marker_pl`
  - This value exists in all list type prompts which by default is an empty space.
    This space is replaced when the choice is selected in multiselect scenario.

### Changes

- Spacing in `checkbox` prompt `enabled_symbol` and `disabled_symbol`
  - If you have customised these values, add an empty space at the end.
- Spacing in `expand` prompt `separator`.
  - If you have customised these values, add an empty space at the end.
- Spacing in `rawlist` prompt `separator`.
  - If you have customised these values, add an empty space at the end.

```python
# v0.1.1
regions = inquirer.checkbox(
    message="Select regions:",
    choices=["us-east-1", "us-east-2"],
    enabled_symbol=">",
    disabled_symbol="<"
).execute()

# v0.2.0
regions = inquirer.checkbox(
    message="Select regions:",
    choices=["us-east-1", "us-east-2"],
    enabled_symbol="> ", # add a space
    disabled_symbol="< " # add a space
).execute()
```

## 0.1.1 (03/04/2021)

### Fixed

- Height and visual glitch on smaller data sets for fuzzy prompt.

## 0.1.0 (17/01/2020)
