"""Servers as another entry point for `InquirerPy`.

See Also:
    :ref:`index:Alternate Syntax`.

`inquirer` directly interact with individual prompt classes. It’s more flexible, easier to customise and also provides IDE type hintings/completions.
"""
from InquirerPy.prompts import CheckboxPrompt as checkbox
from InquirerPy.prompts import ConfirmPrompt as confirm
from InquirerPy.prompts import ExpandPrompt as expand
from InquirerPy.prompts import FilePathPrompt as filepath
from InquirerPy.prompts import FuzzyPrompt as fuzzy
from InquirerPy.prompts import InputPrompt as text
from InquirerPy.prompts import ListPrompt as select
from InquirerPy.prompts import NumberPrompt as number
from InquirerPy.prompts import RawlistPrompt as rawlist
from InquirerPy.prompts import SecretPrompt as secret
