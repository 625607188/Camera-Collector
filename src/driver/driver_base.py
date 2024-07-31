from abc import ABCMeta, abstractmethod
from src.log import log


class DriverBase(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.logger = log.get_logger()

    @abstractmethod
    def config(self, *args):
        pass

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self, s):
        pass

    @abstractmethod
    def recv(self, size):
        pass
