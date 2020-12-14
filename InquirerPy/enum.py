"""Module contains common string."""
from typing import Dict

from prompt_toolkit.enums import EditingMode

ACCEPTED_KEYBINDINGS: Dict[str, EditingMode] = {
    "default": EditingMode.EMACS,
    "emacs": EditingMode.EMACS,
    "vim": EditingMode.VI,
}

INQUIRERPY_KEYBOARD_INTERRUPT: str = "INQUIRERPY_KEYBOARD_INTERRUPT"

INQUIRERPY_POINTER_SEQUENCE: str = "\u276f"
INQUIRERPY_FILL_HEX_SEQUENCE: str = "\u2b22"
INQUIRERPY_EMPTY_HEX_SEQUENCE: str = "\u2b21"
