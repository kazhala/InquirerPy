"""Module contains import of other prompts.

Servers as another entrypoint of constructing a prompt providing
proper type hinting and completions.
"""
from InquirerPy.prompts.checkbox import CheckboxPrompt as checkbox
from InquirerPy.prompts.confirm import ConfirmPrompt as confirm
from InquirerPy.prompts.expand import ExpandPrompt as expand
from InquirerPy.prompts.filepath import FilePathPrompt as filepath
from InquirerPy.prompts.fuzzy.fuzzy import FuzzyPrompt as fuzzy
from InquirerPy.prompts.input import InputPrompt as text
from InquirerPy.prompts.list import ListPrompt as select
from InquirerPy.prompts.rawlist import RawlistPrompt as rawlist
from InquirerPy.prompts.secret import SecretPrompt as secret
