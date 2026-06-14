"""Application package: the singleton entry point and its states."""

from .state import ApplicationState
from .application import Application, application

__all__ = ["Application", "application", "ApplicationState"]
