from json import dumps
from typing import Dict
from enum import Enum
from PyQt6.QtCore import pyqtBoundSignal

from src.business.management.management_command_base import ManagementCommandBase


class SerialCommand(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GET_SSID = "getSsid"
    GET_PASSWORD = "getPassword"
    GET_WIFI_STATUS = "getWifiStatus"
    CONNECT_WIFI = "connectWifi"
    DISCONNECT_WIFI = "disconnectWifi"

    def __str__(self) -> str:
        """Return the string value of the enum member."""
        return self.value


class SerialManagementCommandBase(ManagementCommandBase):
    def __init__(self):
        super(SerialManagementCommandBase, self).__init__()

    def _build_command(self, command_name: SerialCommand, additional_data={}) -> str:
        return dumps(
            {
                "driver": "serial",
                "command": command_name.value,
                **additional_data,
            }
        )


class SerialConnectCommand(SerialManagementCommandBase):
    def __init__(self, com: str, baud: int):
        self.com = com
        self.baud = baud

    def execute(self, handle) -> None:
        message = self._build_command(
            SerialCommand.CONNECT,
            {
                "com": self.com,
                "baud": self.baud,
            },
        )
        handle(message)


class SerialDisconnectCommand(SerialManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SerialCommand.DISCONNECT)
        handle(message)


class SerialGetSsidCommand(SerialManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SerialCommand.GET_SSID)
        handle(message)


class SerialGetPasswordCommand(SerialManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SerialCommand.GET_PASSWORD)
        handle(message)


class SerialGetWifiStatusCommand(SerialManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SerialCommand.GET_WIFI_STATUS)
        handle(message)


class SerialConnectWifiCommand(SerialManagementCommandBase):
    def __init__(self, ssid, password) -> None:
        self.ssid = ssid
        self.password = password

    def execute(self, handle) -> None:
        message = self._build_command(
            SerialCommand.CONNECT_WIFI,
            {
                "ssid": self.ssid,
                "password": self.password,
            },
        )
        handle(message)


class SerialDisconnectWifiCommand(SerialManagementCommandBase):
    def execute(self, handle) -> None:
        message = self._build_command(SerialCommand.DISCONNECT_WIFI)
        handle(message)
