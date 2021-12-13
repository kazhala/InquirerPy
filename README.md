# InquirerPy

[![Test](https://github.com/kazhala/InquirerPy/workflows/Test/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ATest)
[![Lint](https://github.com/kazhala/InquirerPy/workflows/Lint/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ALint)
[![Build](https://codebuild.ap-southeast-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUUYyRUIxOXBWZ0hKcUhrbXplQklMemRsTVBxbUk3bFlTdldnRGpxeEpQSXJidEtmVEVzbVNCTE1UR3VoRSt2N0NQV0VaUXlCUzNackFBNzRVUFBBS1FnPSIsIml2UGFyYW1ldGVyU3BlYyI6IloxREtFeWY4WkhxV0NFWU0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://ap-southeast-2.console.aws.amazon.com/codesuite/codebuild/378756445655/projects/InquirerPy/history?region=ap-southeast-2&builds-meta=eyJmIjp7InRleHQiOiIifSwicyI6e30sIm4iOjIwLCJpIjowfQ)
[![Coverage](https://img.shields.io/coveralls/github/kazhala/InquirerPy?logo=coveralls)](https://coveralls.io/github/kazhala/InquirerPy?branch=master)
[![Version](https://img.shields.io/pypi/pyversions/InquirerPy)](https://pypi.org/project/InquirerPy/)
[![PyPi](https://img.shields.io/pypi/v/InquirerPy)](https://pypi.org/project/InquirerPy/)

Documentation: [inquirerpy.readthedocs.io](https://inquirerpy.readthedocs.io/)

<!-- start intro -->

## Introduction

`InquirerPy` is a Python port of the famous [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/) (A collection of common interactive command line user interfaces).
This project is a re-implementation of the [PyInquirer](https://github.com/CITGuru/PyInquirer) project, with bug fixes of known issues, new prompts, backward compatible APIs
as well as more customisation options.

<!-- end intro -->

![Demo](https://github.com/kazhala/gif/blob/master/InquirerPy-demo.gif)

## Motivation

[PyInquirer](https://github.com/CITGuru/PyInquirer) is a great Python port of [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/), however, the project is slowly reaching
to an unmaintained state with various issues left behind and no intention to implement more feature requests. I was heavily relying on this library for other projects but
could not proceed due to the limitations.

Some noticeable ones that bother me the most:

- hard limit on `prompt_toolkit` version 1.0.3
- various color issues
- various cursor issues
- No options for VI/Emacs navigation key bindings
- Pagination option doesn't work

This project uses python3.7+ type hinting with focus on resolving above issues while providing greater customisation options.

## Requirements

### OS

Leveraging [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit), `InquirerPy` works cross platform for all OS. Although Unix platform may have a better experience than Windows.

### Python

```
python >= 3.7
```

## Getting Started

Checkout full documentation **[here](https://inquirerpy.readthedocs.io/)**.

### Install

```sh
pip3 install InquirerPy
```

### Quick Start

#### Classic Syntax (PyInquirer)

```python
from InquirerPy import prompt

questions = [
    {"type": "input", "message": "What's your name:", "name": "name"},
    {"type": "confirm", "message": "Confirm?", "name": "confirm"},
]
result = prompt(questions)
name = result["name"]
confirm = result["confirm"]
```

#### Alternate Syntax

```python
from InquirerPy import inquirer

name = inquirer.text(message="What's your name:").execute()
confirm = inquirer.confirm(message="Confirm?").execute()
```

<!-- start migration -->

## Migrating from PyInquirer

Most APIs from [PyInquirer](https://github.com/CITGuru/PyInquirer) should be compatible with `InquirerPy`. If you have discovered more incompatible APIs, please
create an issue or directly update README via a pull request.

### EditorPrompt

`InquirerPy` does not support [editor](https://github.com/CITGuru/PyInquirer#editor---type-editor) prompt as of now.

### CheckboxPrompt

The following table contains the mapping of incompatible parameters.

| PyInquirer      | InquirerPy      |
| --------------- | --------------- |
| pointer_sign    | pointer         |
| selected_sign   | enabled_symbol  |
| unselected_sign | disabled_symbol |

### Style

Every style keys from [PyInquirer](https://github.com/CITGuru/PyInquirer) is present in `InquirerPy` except the ones in the following table.

| PyInquirer | InquirerPy |
| ---------- | ---------- |
| selected   | pointer    |

Although `InquirerPy` support all the keys from [PyInquirer](https://github.com/CITGuru/PyInquirer), the styling works slightly different.
Please refer to the [Style](https://inquirerpy.readthedocs.io/en/latest/pages/style.html) documentation for detailed information.

<!-- end migration -->

## Similar projects

### questionary

[questionary](https://github.com/tmbo/questionary) is a fantastic fork which supports `prompt_toolkit` 3.0.0+ with performance improvement and more customisation options.
It's already a well established and stable library.

Comparing with [questionary](https://github.com/tmbo/questionary), `InquirerPy` offers even more customisation options in styles, UI as well as key bindings. `InquirerPy` also provides a new
and powerful [fuzzy](https://inquirerpy.readthedocs.io/en/latest/pages/prompts/fuzzy.html) prompt.

### python-inquirer

[python-inquirer](https://github.com/magmax/python-inquirer) is another great Python port of [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/). Instead of using `prompt_toolkit`, it
leverages the library `blessed` to implement the UI.

Before implementing `InquirerPy`, this library came up as an alternative. It's a more stable library comparing to the original [PyInquirer](https://github.com/CITGuru/PyInquirer), however
it has a rather limited customisation options and an older UI which did not solve the issues I was facing described in the [Motivation](#Motivation) section.

Comparing with [python-inquirer](https://github.com/magmax/python-inquirer), `InquirerPy` offers a slightly better UI,
more customisation options in key bindings and styles, providing pagination as well as more prompts.

## Credit

This project is based on the great work done by the following projects & their authors.

- [PyInquirer](https://github.com/CITGuru/PyInquirer)
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

## License

This project is licensed under [MIT](https://github.com/kazhala/InquirerPy/blob/master/LICENSE).
