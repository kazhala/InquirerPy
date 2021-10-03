"""Module contains base class for prompts.

BaseSimplePrompt ← InputPrompt ← SecretPrompt ...
        ↑
BaseComplexPrompt
        ↑
BaseListPrompt ← FuzzyPrompt
        ↑
ListPrompt ← ExpandPrompt ...
"""

from .complex import BaseComplexPrompt, FakeDocument
from .control import Choice, InquirerPyUIListControl
from .list import BaseListPrompt
from .simple import BaseSimplePrompt
