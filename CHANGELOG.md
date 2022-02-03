# CHANGELOG

Notable changes are documented in this file.

## 0.3.3 (04/02/2021)

- Fixed windows filepath completion [#32](https://github.com/kazhala/InquirerPy/issues/32)

## 0.3.2 (28/01/2021)

- Added exact match option for fuzzy prompt [#34](https://github.com/kazhala/InquirerPy/issues/34)

## 0.3.1 (13/12/2021)

### Fixed

- Fixed InvalidArgument raised for callable default

### Added

- [number prompt](https://inquirerpy.readthedocs.io/en/latest/pages/prompts/number.html)
  - Built for receiving number input
  - Supports decimal
  - Supports negative
  - Non number input is disabled
  - Supports thresholds
- async support [#30](https://github.com/kazhala/InquirerPy/issues/30)
  - [classic syntax](https://inquirerpy.readthedocs.io/en/latest/pages/prompt.html#asynchronous-execution)
  - [alternate syntax](https://inquirerpy.readthedocs.io/en/latest/pages/inquirer.html#asynchronous-execution)

## 0.3.0 (12/10/2021)

**New Documentation: [inquirerpy.readthedocs.io](https://inquirerpy.readthedocs.io/en/latest/)**

### Added

- ~~Added optional spinner to display while loading choices for list prompts~~
- Added parameter `border` for list prompts to display a border around the choices
- Added parameter `long_instruction` to display longer instructions such as keybinding instructions at the bottom [#7](https://github.com/kazhala/InquirerPy/issues/7)
- Added parameter `expand_help` for `expand` prompt to customise the help message and expansion key
  - `help_msg` parameter is deprecated and should use `expand_help`
- Added alternate way of creating choices. Introduced a new class `Choice` as an alternate option for dictionary choice
  - Added `ExpandChoice` for `expand` prompt as well
- Added `raise_keyboard_interrupt` option to all prompt initialisation options
  - The `raise_keyboard_interrupt` in execute function will be deprecated in future releases
- Added parameter `mandatory` and `mandatory_message` to indicate if a prompt can be skipped
- Added ability to skip prompt [#10](https://github.com/kazhala/InquirerPy/issues/10)

### Fixed

- Fixed fuzzy prompt cannot type space [#20](https://github.com/kazhala/InquirerPy/issues/20)
- Fixed multiselect malfunction [#25](https://github.com/kazhala/InquirerPy/issues/25)
- Fixed fuzzy prompt toggle_all [#14](https://github.com/kazhala/InquirerPy/issues/14)

### Changed

- Changed fuzzy prompt `border` default to `False`
  - It was `True` by default, changing this to keep it consistent with other prompts
- Changed style `fuzzy_info` and `instruction` default color to `#abb2bf`
- Automatic spacing added for checkbox prompt, if you have customised the prompt using `enabled_symbol` and `disabled_symbol`,
  you may need to remove the extra space you have previously added. The change here is to align with other prompts current behavior
- Checkbox prompt default value for `enabled_symbol` and `disabled_symbol` is changed from hex symbol to circle [#22](https://github.com/kazhala/InquirerPy/issues/22)
- **Behavior of `raise_keyboard_interrupt` is changed. Checkout the documentation for more info**

## 0.2.4 (12/08/2021)

### Fixed

- Fixed fuzzy prompt choices are centered

## 0.2.3 (04/08/2021)

### Added

- Added option `wrap_lines` to all prompts to configure line wrapping
- Added option `instruction` for non-list type prompts. This is already supported in all list type prompts previously
- Added option `confirm_letter` and `reject_letter` to confirm prompts. Use the 2 value to change from the default "y/n"
  - For updating the result value, please use the `transformer` parameter. By default, no matter what confirm_letter or
    reject letter you set, it will always be Yes or No

```python
from InquirerPy import inquirer

inquirer.confirm(
    message="Proceed?",
    default=True,
    confirm_letter="s",
    reject_letter="n",
    transformer=lambda result: "SIm" if result else "Não",
).execute()
```

### Fixed

- Line wrapping [#11](https://github.com/kazhala/InquirerPy/issues/11)

### Changed

- Answered question prefix spacing now depends on `amark` parameter instead of `qmark`
  - If you previously disable the `qmark` by setting it to empty string, please also set `amark` to empty string

## 0.2.2 (03/07/2021)

N/A

## 0.2.1 (03/07/2021)

### Added

- Added option to disable cycle behavior in list type prompts [#9](https://github.com/kazhala/InquirerPy/issues/9)
- Added parameter `amark`. You can use this value to change the `qmark` after the question is answered
- Added some more style customisation option
  - `answermark`: Used to change the color and style of `amark`
  - `answered_question`: Used to change the color and style of `question` message once the question is answered

## 0.2.0 (01/05/2021)

### Added

- Defaults for multi-select list [#2](https://github.com/kazhala/InquirerPy/issues/2)
- Disable qmark [#3](https://github.com/kazhala/InquirerPy/issues/3)
- Configure `marker_pl`
  - This value exists in all list type prompts which by default is an empty space
    This space is replaced when the choice is selected in multiselect scenario

### Changed

- Spacing in `checkbox` prompt `enabled_symbol` and `disabled_symbol`
  - If you have customised these values, add an empty space at the end
- Spacing in `expand` prompt `separator`
  - If you have customised these values, add an empty space at the end
- Spacing in `rawlist` prompt `separator`
  - If you have customised these values, add an empty space at the end

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

- Height and visual glitch on smaller data sets for fuzzy prompt

## 0.1.0 (17/01/2020)
