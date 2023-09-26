# FAQ

## Can I change how the user answer is displayed?

```{seealso}
{ref}`pages/dynamic:transformer`
```

Yes, especially for list type prompts with multiple selection, printing selection
as a list is not ideal in a lot of scenarios. Use `transformer` parameter to customise it.

## How can I do unittest when using `InquirerPy`?

```{tip}
Since `InquirerPy` module itself is tested, there's no need to mock any further/deeper than the API entrypoint (`prompt` and `inquirer`).
```

For {ref}`index:Classic Syntax (PyInquirer)` user, it would be just a direct mock on the {ref}`pages/prompt:prompt` function.

```{code-block} python
---
caption: Module/somefunction.py
---
from InquirerPy import prompt

def get_name():
    return prompt({"type": "input", "message": "Name:"})
```

```{code-block} python
---
caption: tests/test_somefunction.py
---
import unittest
from unittest.mock import patch

from Module.somefunction import get_name

class TestPrompt(unittest.TestCase):
    @patch("Module.somefunction.prompt")
    def test_get_name(self, mocked_prompt):
        mocked_prompt.return_value = "hello"
        result = get_name()
        self.assertEqual(result, "hello")
```

For {ref}`index:Alternate Syntax` user, you'd have to mock 1 level deeper to the prompt class level.

```{code-block} python
---
caption: Module/somefunction.py
---
from InquirerPy import inquirer

def get_name():
    return inquirer.text(message="Name:").execute()
```

```{code-block} python
---
caption: tests/test_somefunction.py
---
import unittest
from unittest.mock import patch

from Module.somefunction import get_name

class TestPrompt(unittest.TestCase):
    @patch("Module.somefunction.inquirer.text")
    def test_get_name(self, mocked_prompt):
        mocked_prompt.return_value = "hello"
        result = get_name()
        self.assertEqual(result, "hello")
```

## Can I navigate back to the previous question?

No. With the current implementation this is not possible since the control of the prompt is terminated after it is answered.
This may be supported in the future but not a priority at the moment.
