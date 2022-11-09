"""Module contains base class for prompts.

BaseSimplePrompt ← InputPrompt ← SecretPrompt ...
        ↑
BaseComplexPrompt
        ↑
BaseListPrompt ← FuzzyPrompt
        ↑
ListPrompt ← ExpandPrompt ...
"""

__all__ = [
    "BaseComplexPrompt",
    "FakeDocument",
    "Choice",
    "InquirerPyUIListControl",
    "BaseSimplePrompt",
    "BaseListPrompt",
]

from .complex import BaseComplexPrompt, FakeDocument
from .control import Choice, InquirerPyUIListControl
from .list import BaseListPrompt
from .simple import BaseSimplePrompt
