"""Top-level application states."""

from enum import Enum, auto


class ApplicationState(Enum):
    SPLASH = auto()
    MENU = auto()
    MATCH = auto()
