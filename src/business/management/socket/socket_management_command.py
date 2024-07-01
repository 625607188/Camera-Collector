from enum import Enum
import json
from PyQt6.QtCore import pyqtBoundSignal

from src.business.management.management_command_base import ManagementCommandBase


class SocketCommand(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GET_CONFIG = "get_config"
    SET_CONFIG = "set_config"
    CONTROL = "control"
    UPGRADE = "upgrade"
    PING = "ping"


class SocketManagementCommandBase(ManagementCommandBase):
    def _build_command(
        self, command_name: SocketCommand, additional_data: dict = {}
    ) -> str:
        command_data = {
            "driver": "socket",
            "command": command_name.value,
            **additional_data,
        }
        return json.dumps(command_data)


class SocketConnectCommand(SocketManagementCommandBase):
    def __init__(self, uuid: str) -> None:
        self.uuid = uuid

    def execute(self, handle) -> None:
        message = self._build_command(SocketCommand.CONNECT, {"uuid": self.uuid})
        handle(message)


class SocketDisconnectCommand(SocketManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SocketCommand.DISCONNECT)
        handle(message)


class SocketGetConfigCommand(SocketManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SocketCommand.GET_CONFIG)
        handle(message)


class SocketSetConfigCommand(SocketManagementCommandBase):
    def __init__(self, config) -> None:
        self.config = config

    def execute(self, handle) -> None:
        message = self._build_command(SocketCommand.SET_CONFIG, {"config": self.config})
        handle(message)


class SocketControlCommand(SocketManagementCommandBase):
    def __init__(self, control) -> None:
        self.control = control

    def execute(self, handle) -> None:
        message = self._build_command(SocketCommand.CONTROL, {"control": self.control})
        handle(message)


class SocketUpgradeCommand(SocketManagementCommandBase):
    def __init__(self, filePath) -> None:
        self.filePath = filePath

    def execute(self, handle) -> None:
        message = self._build_command(
            SocketCommand.UPGRADE, {"filePath": self.filePath}
        )
        handle(message)
