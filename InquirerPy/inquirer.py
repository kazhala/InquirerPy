"""Module contains import of other prompts.

Servers as another entrypoint of constructing a prompt providing
proper type hinting and completions.
"""
from InquirerPy.prompts import CheckboxPrompt as checkbox
from InquirerPy.prompts import ConfirmPrompt as confirm
from InquirerPy.prompts import ExpandPrompt as expand
from InquirerPy.prompts import FilePathPrompt as filepath
from InquirerPy.prompts import FuzzyPrompt as fuzzy
from InquirerPy.prompts import InputPrompt as text
from InquirerPy.prompts import ListPrompt as select
from InquirerPy.prompts import RawlistPrompt as rawlist
from InquirerPy.prompts import SecretPrompt as secret
