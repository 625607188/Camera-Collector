from json import loads
from typing import List
from PyQt6.QtCore import QObject, pyqtSignal

from src.business.management.socket.socket_management_command import (
    SocketConnectCommand,
    SocketDisconnectCommand,
    SocketUpgradeCommand,
)
from src.common.thread.create_thread import create_and_start_thread
from src.log import log
from src.business.management.driver_info import DriverInfo
from src.business.management.socket.socket_management import SocketManagement
from src.business.management.driver_wifi.wifi_scanner import WifiScanner
from src.business.management.serial.serial_management import SerialManagement


class DriverManagement(QObject):
    control_serial_signal = pyqtSignal(str)

    def __init__(
        self,
        parent,
        display_warning_signal,
        display_socket_status_change_signal,
        display_socket_search_signal,
        display_socket_picture_signal,
        display_serial_list_signal,
        display_serial_status_change_signal,
        display_wifi_ssid_list_signal,
        display_wifi_ssid_signal,
        display_wifi_password_signal,
        display_wifi_enable_signal,
        display_wifi_connect_status_signal,
    ) -> None:
        super(DriverManagement, self).__init__(parent)

        self.display_warning_signal = display_warning_signal
        self.display_socket_status_change_signal = display_socket_status_change_signal
        self.display_socket_search_signal = display_socket_search_signal
        self.display_socket_picture_signal = display_socket_picture_signal
        self.display_serial_list_signal = display_serial_list_signal
        self.display_serial_status_change_signal = display_serial_status_change_signal
        self.display_wifi_ssid_list_signal = display_wifi_ssid_list_signal
        self.display_wifi_ssid_signal = display_wifi_ssid_signal
        self.display_wifi_password_signal = display_wifi_password_signal
        self.display_wifi_enable_signal = display_wifi_enable_signal
        self.display_wifi_connect_status_signal = display_wifi_connect_status_signal

        self.logger = log.get_logger()
        self.info = DriverInfo()

        self.start_socket_management_thread()
        self.start_serial_management_thread()
        self.start_wifi_scanner_thread()

    def deleteLater(self):
        self.socketManagementQThread.quit()
        self.socketManagementQThread.quit()

    def notify_warning(self, warning) -> None:
        self.display_warning_signal.emit(warning)

    def handle_message(self, message: str) -> None:
        message_dict = loads(message)
        if message_dict["driver"] == "socket":
            self.socketManagement.control_signal.emit(message)
        elif message_dict["driver"] == "serial":
            self.control_serial_signal.emit(message)

    def display_warning_event(self, warning) -> None:
        self.display_warning_signal.emit(warning)

    def display_socket_status_change_event(self, status) -> None:
        self.display_socket_status_change_signal.emit(status)

    def display_socket_search_event(self, result) -> None:
        self.display_socket_search_signal.emit(result)

    def display_socket_picture_event(self, image) -> None:
        self.display_socket_picture_signal.emit(image)

    def start_socket_management_thread(self) -> None:
        self.socketManagement = SocketManagement()
        self.socketManagement.set_callback(
            self.display_warning_event,
            self.display_socket_status_change_event,
            self.display_socket_search_event,
            self.display_socket_picture_event,
        )

        self.socketManagementQThread = create_and_start_thread(self.socketManagement)

    def socket_connect(self, uuid: str) -> None:
        invoker = SocketConnectCommand(uuid)
        invoker.execute(self.handle_message)

    def socket_disconnect(self) -> None:
        invoker = SocketDisconnectCommand()
        invoker.execute(self.handle_message)

    def socket_upgrade(self, filePath) -> None:
        invoker = SocketUpgradeCommand(filePath)
        invoker.execute(self.handle_message)

    def display_serial_list_event(self, serial_list) -> None:
        self.display_serial_list_signal.emit(serial_list)

    def display_serial_status_change_event(self, status) -> None:
        self.display_serial_status_change_signal.emit(status)

    def display_wifi_ssid_event(self, ssid) -> None:
        self.display_wifi_ssid_signal.emit(ssid)

    def display_wifi_password_event(self, password) -> None:
        self.display_wifi_password_signal.emit(password)

    def display_wifi_enbale_event(self, enable) -> None:
        self.display_wifi_enable_signal.emit(enable)

    def display_wifi_connect_status_event(self, status) -> None:
        self.display_wifi_connect_status_signal.emit(status)

    def start_serial_management_thread(self) -> None:
        self.serialManagement = SerialManagement()
        self.serialManagement.set_callback(
            self.display_warning_event,
            self.display_serial_list_event,
            self.display_serial_status_change_event,
            self.display_wifi_ssid_event,
            self.display_wifi_password_event,
            self.display_wifi_enbale_event,
            self.display_wifi_connect_status_event)

        self.serialManagementQThread = create_and_start_thread(self.serialManagement)

    def serial_connect(self, com, baud) -> None:
        self.serialManagement.connect(com, baud)

    def serial_disconnect(self) -> None:
        self.serialManagement.disconnect()

    def display_wifi_ssid_list_event(self, ssidList) -> None:
        self.display_wifi_ssid_list_signal.emit(ssidList)

    def start_wifi_scanner_thread(self) -> None:
        self.wifiScanner = WifiScanner()
        self.wifiScanner.set_callback(self.display_wifi_ssid_list_event)

        self.wifiScannerQThread = create_and_start_thread(self.wifiScanner)
