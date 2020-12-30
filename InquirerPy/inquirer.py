"""Module contains import of other prompts.

Servers as another entrypoint of constructing a prompt providing
proper type hinting and completions.
"""
from InquirerPy.prompts import (
    CheckboxPrompt as checkbox,
    ConfirmPrompt as confirm,
    ExpandPrompt as expand,
    FilePathPrompt as filepath,
    FuzzyPrompt as fuzzy,
    InputPrompt as text,
    ListPrompt as select,
    RawlistPrompt as rawlist,
    SecretPrompt as secret,
)
