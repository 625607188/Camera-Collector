import json
from typing import Optional
from PyQt6.QtCore import Qt, QObject, QTimer, pyqtSignal, pyqtSlot
from src.driver.driver_serial import camera_serial
from src.driver.driver_serial.camera_serial.camera_serial_command import (
    set_wifi_enable_command,
)
from src.log import log
from src.driver.driver_factory import SERIAL_PRODUCT, DriverFactory
from src.business.management.serial.serial_management_command import SerialCommand
from src.driver.driver_serial.camera_serial.camera_serial import CameraSerial
from serial import Serial
from serial.tools.list_ports import comports


class SerialManagement(QObject):
    control_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super(SerialManagement, self).__init__(parent)

        self.logger = log.get_logger()
        self.timerList = []
        self.robot: Optional[CameraSerial] = None
        self.timer = None
        self.cameraSerial = None

        self.command_handlers = {
            SerialCommand.CONNECT.value: self.connect,
            SerialCommand.DISCONNECT.value: self.disconnect,
            SerialCommand.GET_SSID.value: self.get_ssid,
            SerialCommand.GET_PASSWORD.value: self.get_password,
            SerialCommand.GET_WIFI_STATUS.value: self.get_wifi_status,
            SerialCommand.CONNECT_WIFI.value: self.connect_wifi,
            SerialCommand.DISCONNECT_WIFI.value: self.disconnect_wifi,
        }

    def set_callback(
        self, notify_warning, notify_serial_list, notify_serial_status_change
    ) -> None:
        self.notify_warning_callback = notify_warning
        self.notify_serial_list_callback = notify_serial_list
        self.notify_serial_status_change_callback = notify_serial_status_change

    def scan_serial_list(self) -> None:
        serials = {}
        ports = comports()
        for port, desc, _ in ports:
            if "蓝牙" in desc:
                continue
            serials[port] = desc
        self.serialDict = serials
        self.notify_serial_list_callback(serials.values())

    def timerEvent(self, event):
        for timer, call in self.timerList:
            if event.timerId() == timer:
                call()

    @pyqtSlot()
    def run(self) -> None:
        self.control_signal.connect(self.handle_message)

        self.scanSerialTimer = self.startTimer(2000, Qt.TimerType.PreciseTimer)
        self.timerList.append((self.scanSerialTimer, lambda: self.scan_serial_list()))

        self.thread().exec()

        self.thread().quit()

    def deleteLater(self):
        for timer, _ in self.timerList:
            self.killTimer(timer)
        self.timerList.clear()

    def connect(self, comDesp, baud) -> None:
        com = next(
            (key for key, value in self.serialDict.items() if value == comDesp), None
        )
        if com is None:
            self.notify_warning_callback("串口不存在")
            return

        try:
            self.cameraSerial = DriverFactory.create(SERIAL_PRODUCT, com, baud)
            if self.cameraSerial is None:
                self.notify_warning_callback("串口连接失败")
                self.notify_serial_status_change_callback(False)
                return

            self.notify_serial_status_change_callback(True)
            self.get_ssid()
            self.get_password()
            self.get_wifi_status()

        except Exception as e:
            self._handle_exception(e)

    def disconnect(self):
        try:
            if self.cameraSerial:
                self.cameraSerial.close()
                del self.cameraSerial
            self.cameraSerial = None
            self.notify_serial_status_change_callback(False)
        except Exception as e:
            pass

    def connect_wifi_task(self, ssid, password):
        self.cameraSerial.set_ssid(ssid)
        self.cameraSerial.set_password(password)
        self.cameraSerial.set_wifi_enable(True)

    def connect_wifi(self, ssid, password):
        self.cameraSerial.set_wifi_enable(False)

        timer = QTimer()
        timer.timeout.connect(lambda: self.connect_wifi_task(ssid, password))
        timer.setSingleShot(True)
        timer.start(1000)

    def disconnect_wifi(self):
        self.cameraSerial.set_wifi_enable(False)

    def get_ssid(self) -> None:
        # TODO
        ssid = self.cameraSerial.get_ssid()

    def get_password(self) -> None:
        pass

    def get_wifi_status(self) -> None:
        pass

    @pyqtSlot(str)
    def handle_message(self, message) -> None:
        try:
            messageDict = json.loads(message)
            command = messageDict.get("command")
            handler = self.command_handlers.get(command)

            if handler:
                if command in (
                    SerialCommand.DISCONNECT.value,
                    SerialCommand.GET_SSID.value,
                    SerialCommand.GET_PASSWORD.value,
                    SerialCommand.GET_WIFI_STATUS.value,
                    SerialCommand.DISCONNECT_WIFI.value,
                ):
                    handler()
                elif command == SerialCommand.CONNECT.value:
                    handler(
                        messageDict["com"],
                        messageDict["baud"],
                    )
                elif command == SerialCommand.CONNECT_WIFI.value:
                    handler(
                        messageDict["ssid"],
                        messageDict["password"],
                    )
                else:
                    self.logger.error(f"未定义参数处理逻辑的命令 '{command}'.")
            else:
                self.logger.error(f"收到未知命令: {command}")
        except json.JSONDecodeError:
            self.logger.error("接收到无效的JSON消息。")
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception(self, exception):
        self.logger.error(f"发生错误: {exception}")
        if self.cameraSerial:
            self.cameraSerial.close()
            self.cameraSerial = None
        self.notify_warning_callback(f"操作失败: {exception}")
        self.notify_serial_status_change_callback(False)
