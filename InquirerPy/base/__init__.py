"""Module contains base class for prompts.

BaseSimplePrompt ← InputPrompt, 
        ↑               ↑
        ↑          SecretPrompt ...
        ↑
BaseComplexPrompt ← FuzzyPrompt
        ↑
BaseListPrompt ← ListPrompt, ExpandPrompt ...
"""

from .complex import BaseComplexPrompt, FakeDocument
from .control import InquirerPyUIControl
from .list import BaseListPrompt
from .simple import BaseSimplePrompt
