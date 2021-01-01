# InquirerPy

[![Test](https://github.com/kazhala/InquirerPy/workflows/Test/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ATest)
[![Lint](https://github.com/kazhala/InquirerPy/workflows/Lint/badge.svg)](https://github.com/kazhala/InquirerPy/actions?query=workflow%3ALint)
[![Build](https://codebuild.ap-southeast-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiUUYyRUIxOXBWZ0hKcUhrbXplQklMemRsTVBxbUk3bFlTdldnRGpxeEpQSXJidEtmVEVzbVNCTE1UR3VoRSt2N0NQV0VaUXlCUzNackFBNzRVUFBBS1FnPSIsIml2UGFyYW1ldGVyU3BlYyI6IloxREtFeWY4WkhxV0NFWU0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://ap-southeast-2.console.aws.amazon.com/codesuite/codebuild/378756445655/projects/InquirerPy/history?region=ap-southeast-2&builds-meta=eyJmIjp7InRleHQiOiIifSwicyI6e30sIm4iOjIwLCJpIjowfQ)

## Introduction

`InquirerPy` is a Python port of the infamous [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/) (A collection of common interactive command line user interfaces).
This project is a re-implementation of the [PyInquirer](https://github.com/CITGuru/PyInquirer) project, with bug fixes of known issues, new prompts, backward compatible APIs
as well as more customization options.

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

## Similar projects

### questionary

While developing this project, I've discovered there's already another re-implementation of [PyInquirer](https://github.com/CITGuru/PyInquirer) called [questionary](https://github.com/tmbo/questionary).
It's a fantastic fork which supports `prompt_toolkit` 3.0.0+ with performance improvement and more customization options. It's already a well established and stable library.

Comparing with [questionary](https://github.com/tmbo/questionary), `InquirerPy` offers even more customization options in styles, UI as well as key bindings. `InquirerPy` also provides a new
and powerful [fuzzy]() prompt.

If you are already using questionary, I do not suggest using `InquirerPy` unless you require more customization or wanna try out the [fuzzy]() prompt as both library is not API compatible.

### python-inquirer

[python-inquirer](https://github.com/magmax/python-inquirer) is another great Python port of [Inquirer.js](https://github.com/SBoudrias/Inquirer.js/). Instead of using `prompt_toolkit`, it
leverages the library `blessed` to implement the UI.

Before implementing `InquirerPy`, this library came up as an alternative. It's a more stable library comparing to the original [PyInquirer](https://github.com/CITGuru/PyInquirer), however
it has a rather limited customization options and an older UI which did not solve the issues I'm facing described in the [Motivation](#Motivation) section.

Comparing with [python-inquirer](https://github.com/magmax/python-inquirer), `InquirerPy` offers a slightly better UI,
more customization options in key bindings and styles, providing pagination as well as more prompts.
