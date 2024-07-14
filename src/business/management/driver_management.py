from json import loads
from typing import List
from PyQt6.QtCore import QObject, pyqtSignal

from src.business.management.socket.socket_management_command import (
    SocketConnectCommand,
    SocketDisconnectCommand,
    SocketUpgradeCommand,
    SocketGetConfigCommand,
    SocketSetConfigCommand,
)
from src.common.thread.create_thread import create_and_start_thread
from src.log import log
from src.business.management.driver_info import DriverInfo
from src.business.management.socket.socket_management import SocketManagement


class DriverManagement(QObject):
    control_serial_signal = pyqtSignal(str)

    def __init__(
        self,
        parent,
        display_warning_signal,
        display_socket_status_change_signal,
        display_socket_picture_signal,
        display_socket_config_signal,
    ) -> None:
        super(DriverManagement, self).__init__(parent)

        self.display_warning_signal = display_warning_signal
        self.display_socket_status_change_signal = display_socket_status_change_signal
        self.display_socket_picture_signal = display_socket_picture_signal
        self.display_socket_config_signal = display_socket_config_signal

        self.logger = log.get_logger()
        self.info = DriverInfo()

        self.start_socket_management_thread()

    def deleteLater(self):
        self.socketManagementQThread.quit()
        self.socketManagementQThread.quit()

    def notify_warning(self, warning) -> None:
        self.display_warning_signal.emit(warning)

    def handle_message(self, message: str) -> None:
        message_dict = loads(message)
        if message_dict["driver"] == "socket":
            self.socketManagement.control_signal.emit(message)

    def display_warning_event(self, warning) -> None:
        self.display_warning_signal.emit(warning)

    def display_socket_status_change_event(self, status) -> None:
        self.display_socket_status_change_signal.emit(status)

    def display_socket_picture_event(self, image) -> None:
        self.display_socket_picture_signal.emit(image)

    def display_socket_config_event(self, config) -> None:
        self.display_socket_config_signal.emit(config)

    def start_socket_management_thread(self) -> None:
        self.socketManagement = SocketManagement()
        self.socketManagement.set_callback(
            self.display_warning_event,
            self.display_socket_status_change_event,
            self.display_socket_picture_event,
            self.display_socket_config_event,
        )

        self.socketManagementQThread = create_and_start_thread(self.socketManagement)

    def socket_connect(self, ip: str, port: int) -> None:
        invoker = SocketConnectCommand(ip, port)
        invoker.execute(self.handle_message)

    def socket_disconnect(self) -> None:
        invoker = SocketDisconnectCommand()
        invoker.execute(self.handle_message)

    def socket_upgrade(self, filePath) -> None:
        invoker = SocketUpgradeCommand(filePath)
        invoker.execute(self.handle_message)

    def socket_get_config(self) -> None:
        invoker = SocketGetConfigCommand()
        invoker.execute(self.handle_message)

    def socket_set_config(self, config) -> None:
        invoker = SocketSetConfigCommand(config)
        invoker.execute(self.handle_message)
