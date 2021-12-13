# InquirerPy

```{include} ../README.md
:start-after: <!-- start intro -->
:end-before: <!-- end intro -->
```

![Demo](https://assets.kazhala.me/InquirerPy/InquirerPy-demo.gif)

## Install

```{admonition} Requirements
python >= 3.7
```

```
pip3 install InquirerPy
```

## Basic Usage

`InquirerPy` provides two types of syntax that you can choose to use: [Classic syntax](#classic-syntax-pyinquirer) and [Alternate Syntax](#alternate-syntax).

```{Tip}
For any new users, [Alternate Syntax](#alternate-syntax) is recommended as its more flexible and extensible.
```

```{Note}
Checkout the sidebar on the left for detailed explanation and usage.
```

### Classic Syntax (PyInquirer)

```{Note}
Syntax ported from [PyInquirer](https://github.com/CITGuru/PyInquirer) which allows easy transition between the two projects.
Checkout [migration guide](#migrating-from-pyinquirer).
```

```{eval-rst}
The :ref:`pages/prompt:prompt` function takes a list of questions and return the result.
Each question should be an instance of :class:`dict`. Different types of `prompt` could require different keys, please
refer to individual `prompt` documentation for detailed explanation.
```

As a rule of thumb, each question requires a `type` (type of prompt) and `message` (question to ask) key. For any `prompt`
involving lists, a `choices` (list of available choices) key is also required.

Optionally provide a `name` key, `prompt` will store the result under the provided name key in the final result. If
no `name` key is provided, the index of the question will be used.

```python
from InquirerPy import prompt

questions = [
    {"type": "input", "message": "What's your name:", "name": "name"},
    {
        "type": "list",
        "message": "What's your favourite programming language:",
        "choices": ["Go", "Python", "Rust", "JavaScript"],
    },
    {"type": "confirm", "message": "Confirm?"},
]
result = prompt(questions)
name = result["name"]
fav_lang = result[1]
confirm = result[2]
```

### Alternate Syntax

Alternate syntax directly interact with individual `prompt` classes. It's more flexible, easier to customise
and also provides IDE type hintings/completions.

```python
from InquirerPy import inquirer

name = inquirer.text(message="What's your name:").execute()
fav_lang = inquirer.select(
    message="What's your favourite programming language:",
    choices=["Go", "Python", "Rust", "JavaScript"],
).execute()
confirm = inquirer.confirm(message="Confirm?").execute()
```

## Detailed Usage

```{admonition} Info
Please visit the sidebar on the left.
```

## Running Examples

`InquirerPy` provides several examples that you can run and play around.

1. Clone the repository

```
git clone https://github.com/kazhala/InquirerPy.git
cd InquirerPy
```

2. Create a Virtual Environment (Recommended)

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```
pip3 install -r examples/requirements.txt
```

4. View all available examples

```{Warning}
`demo_alternate.py` and `demo_classic.py` requires [boto3](https://github.com/boto/boto3) package and setup AWS credentials.
```

```
ls examples/*.py
ls examples/classic/*.py
ls examples/alternate/*.py
```

5. Edit and run any examples of your choice

```
python3 -m examples.classic.rawlist
# or
python3 examples/classic/rawlist
```

```{include} ../README.md
:start-after: <!-- start migration -->
:end-before: <!-- end migration -->
```

```{toctree}
:caption: prompts
:hidden:

pages/prompts/input.md
pages/prompts/secret.md
pages/prompts/filepath.md
pages/prompts/number.md
pages/prompts/confirm.md
pages/prompts/list.md
pages/prompts/rawlist.md
pages/prompts/expand.md
pages/prompts/checkbox.md
pages/prompts/fuzzy.md
```

```{toctree}
:caption: Customisation
:hidden:

pages/style.md
pages/kb.md
pages/height.md
pages/env.md
pages/dynamic.md
pages/raise_kbi.md
```

```{toctree}
:caption: API
:hidden:

pages/inquirer.md
pages/prompt.md
pages/validator.md
pages/separator.md
pages/patched_print.md
pages/color_print.md
```

```{toctree}
:caption: Reference
:hidden:

pages/faq.md
pages/api.md
pages/changelog.md
GitHub Repository <https://github.com/kazhala/InquirerPy>
```
