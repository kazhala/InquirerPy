# InquirerPy

[![Test](https://github.com/kazhala/InquirerPy/workflows/Test/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ATest)
[![Lint](https://github.com/kazhala/InquirerPy/workflows/Lint/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ALint)
[![Build](https://codebuild.ap-southeast-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUUYyRUIxOXBWZ0hKcUhrbXplQklMemRsTVBxbUk3bFlTdldnRGpxeEpQSXJidEtmVEVzbVNCTE1UR3VoRSt2N0NQV0VaUXlCUzNackFBNzRVUFBBS1FnPSIsIml2UGFyYW1ldGVyU3BlYyI6IloxREtFeWY4WkhxV0NFWU0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://ap-southeast-2.console.aws.amazon.com/codesuite/codebuild/378756445655/projects/InquirerPy/history?region=ap-southeast-2&builds-meta=eyJmIjp7InRleHQiOiIifSwicyI6e30sIm4iOjIwLCJpIjowfQ)
[![Version](https://img.shields.io/pypi/pyversions/InquirerPy)](https://pypi.org/project/InquirerPy/)
[![PyPi](https://img.shields.io/pypi/v/InquirerPy)](https://pypi.org/project/InquirerPy/)
[![License](https://img.shields.io/pypi/l/InquirerPy)](https://github.com/kazhala/InquirerPy/blob/master/LICENSE)

Documentation: https://github.com/kazhala/InquirerPy/wiki

## Introduction

`InquirerPy` is a Python port of the famous [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/) (A collection of common interactive command line user interfaces).
This project is a re-implementation of the [PyInquirer](https://github.com/CITGuru/PyInquirer) project, with bug fixes of known issues, new prompts, backward compatible APIs
as well as more customization options.

↓↓↓ Simple AWS S3 uploader/downloader prompt.

![Demo](https://github.com/kazhala/gif/blob/master/InquirerPy-demo.gif)

<details>
  <summary>Classic Syntax (PyInquirer)</summary>

```python
import boto3
from InquirerPy import prompt
from InquirerPy.validator import PathValidator

client = boto3.client("s3")

def get_bucket(_):
    return [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]

def walk_s3_bucket(result):
    response = []
    paginator = client.get_paginator("list_objects")
    for result in paginator.paginate(Bucket=result["bucket"]):
        for file in result["Contents"]:
            response.append(file["Key"])
    return response

def is_upload(result):
    return result[0] == "Upload"

questions = [
    {
        "message": "Select an S3 action:",
        "type": "list",
        "choices": ["Upload", "Download"],
    },
    {
        "message": "Enter the filepath to upload:",
        "type": "filepath",
        "when": is_upload,
        "validate": PathValidator(),
        "only_files": True,
    },
    {
        "message": "Select a bucket:",
        "type": "fuzzy",
        "choices": get_bucket,
        "name": "bucket",
    },
    {
        "message": "Select files to download:",
        "type": "fuzzy",
        "when": lambda _: not is_upload(_),
        "choices": walk_s3_bucket,
        "multiselect": True,
    },
    {
        "message": "Enter destination folder:",
        "type": "filepath",
        "when": lambda _: not is_upload(_),
        "only_directories": True,
        "validate": PathValidator(),
    },
    {"message": "Confirm?", "type": "confirm", "default": False},
]

result = prompt(questions, vi_mode=True)

# Download or Upload the file based on result ...
```

</details>

<details>
  <summary>Alternative Syntax</summary>

```python
import os
import boto3
from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

client = boto3.client("s3")
os.environ["INQUIRERPY_VI_MODE"] = 'true'

def get_bucket(_):
    return [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]

def walk_s3_bucket(bucket):
    response = []
    paginator = client.get_paginator("list_objects")
    for result in paginator.paginate(Bucket=bucket):
        for file in result["Contents"]:
            response.append(file["Key"])
    return response

action = inquirer.select(
    message="Select an S3 action:", choices=["Upload", "Download"]
).execute()

if action == "Upload":
    file_to_upload = inquirer.filepath(
        message="Enter the filepath to upload:",
        validate=PathValidator(),
        only_files=True,
    ).execute()
    bucket = inquirer.fuzzy(message="Select a bucket:", choices=get_bucket).execute()
else:
    bucket = inquirer.fuzzy(message="Select a bucket:", choices=get_bucket).execute()
    file_to_download = inquirer.fuzzy(
        message="Select files to download:",
        choices=lambda _: walk_s3_bucket(bucket),
        multiselect=True,
    ).execute()
    destination = inquirer.filepath(
        message="Enter destination folder:",
        only_directories=True,
        validate=PathValidator(),
    ).execute()

confirm = inquirer.confirm(message="Confirm?").execute()

# Download or Upload the file based on result ...
```

</details>

## Motivation

[PyInquirer](https://github.com/CITGuru/PyInquirer) is a great Python port of [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/), however the project is slowly reaching
to an unmaintained state with various issues left behind and no intention to implement more feature requests. I was heavily relying on this library for other projects but
could not proceed due to the limitations.

Some noticeable ones that bothers me the most:

- hard limit on `prompt_toolkit` version 1.0.3 (current release)
- color issues (unreleased)
- cursor issues (unreleased)
- No options for VI/Emacs navigation key bindings
- Pagination options doesn't work

This project uses python3.7+ type hinting with focus on resolving above issues while providing greater customization options.

## Requirements

### OS

Leveraging `prompt_toolkit`, `InquirerPy` works cross platform for all OS. Although Unix platform may have a better experience than Windows.

### Python

`InquirerPy` requires Python3.7+.

## Getting Started

Checkout full documentation **[here](https://github.com/kazhala/InquirerPy/wiki)**.

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

name = inquirer.text(message="What's your name:")
confirm = inquirer.confirm(message="Confirm?")
```

## Migrating from PyInquirer

Most APIs from `PyInquirer` should be compatible with `InquirerPy`. If you discovered any more incompatible APIs, please
let me know via issues or directly update README via pull request.

### CheckboxPrompt

The following table containing the mapping of the incompatible parameters.

| PyInquirer      | InquirerPy      |
| --------------- | --------------- |
| pointer_sign    | pointer         |
| selected_sign   | enabled_symbol  |
| unselected_sign | disabled_symbol |

### Style

Every style keys from `PyInquirer` is present in `InquirerPy` except the once in the following table.

| PyInquirer | InquirerPy |
| ---------- | ---------- |
| selected   | pointer    |

Although `InquirerPy` support all the keys from `PyInquirer`, the styling works slightly different. Please refer to the [Style](https://github.com/kazhala/InquirerPy/wiki/Style) documentation for detailed information.

## Similar projects

### questionary

While developing this project, I've discovered there's already another re-implementation of [PyInquirer](https://github.com/CITGuru/PyInquirer) called [questionary](https://github.com/tmbo/questionary).
It's a fantastic fork which supports `prompt_toolkit` 3.0.0+ with performance improvement and more customization options. It's already a well established and stable library.

_Unfortunately, the discovery of this project is a little too late since I really believe this is a great project and brings just what I needed to solve my issues with `PyInquirer` and
I may not proceed to develop `InquirerPy`._

Comparing with [questionary](https://github.com/tmbo/questionary), `InquirerPy` offers even more customization options in styles, UI as well as key bindings. `InquirerPy` also provides a new
and powerful [fuzzy](https://github.com/kazhala/InquirerPy/wiki/FuzzyPrompt) prompt.

If you are already using questionary, I do not suggest using `InquirerPy` unless you require more customization or wanna try out the [fuzzy](https://github.com/kazhala/InquirerPy/wiki/FuzzyPrompt) prompt as both library is not API compatible.

### python-inquirer

[python-inquirer](https://github.com/magmax/python-inquirer) is another great Python port of [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/). Instead of using `prompt_toolkit`, it
leverages the library `blessed` to implement the UI.

Before implementing `InquirerPy`, this library came up as an alternative. It's a more stable library comparing to the original [PyInquirer](https://github.com/CITGuru/PyInquirer), however
it has a rather limited customization options and an older UI which did not solve the issues I was facing described in the [Motivation](#Motivation) section.

Comparing with [python-inquirer](https://github.com/magmax/python-inquirer), `InquirerPy` offers a slightly better UI,
more customization options in key bindings and styles, providing pagination as well as more prompts.

## Credit

This project is based on the great work done by the following projects & their authors.

- [PyInquirer](https://github.com/CITGuru/PyInquirer)
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- [sweep.py](https://github.com/aslpavel/sweep.py)

## License

This project is licensed under [MIT](https://github.com/kazhala/InquirerPy/blob/master/LICENSE). Copyright (c) 2020 Kevin Zhuang

The [fzy](https://github.com/kazhala/InquirerPy/blob/master/InquirerPy/prompts/fuzzy/fzy.py) code is licensed under [MIT](https://github.com/aslpavel/sweep.py/blob/master/LICENSE). Copyright (c) 2018 Pavel Aslanov
