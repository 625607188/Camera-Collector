from abc import ABC, abstractmethod
from PyQt6.QtCore import pyqtBoundSignal


class ManagementCommandBase(ABC):
    @abstractmethod
    def execute(self, signal: pyqtBoundSignal) -> None:
        pass
