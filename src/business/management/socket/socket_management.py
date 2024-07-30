from typing import Optional
import json
from PyQt6.QtCore import Qt, QThread, QObject, pyqtSignal, pyqtSlot
from src.common.thread.create_thread import create_and_start_thread
from src.driver.driver_socket.camera_socket.camera_socket import CameraSocket
from src.log import log
from src.driver.driver_factory import SOCKET_PRODUCT, DriverFactory
from src.business.management.socket.socket_management_command import SocketCommand
from src.driver.driver_socket.camera_socket.camera_server import CameraServer


class SocketManagement(QObject):
    control_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super(SocketManagement, self).__init__(parent)

        self.logger = log.get_logger()
        self.timerList = []
        self.robot: Optional[CameraSocket] = None
        self.timer = None
        self.cameraSocket = None

        self.command_handlers = {
            SocketCommand.CONNECT.value: self.connect,
            SocketCommand.DISCONNECT.value: self.disconnect,
            SocketCommand.GET_CONFIG.value: self.get_config,
            SocketCommand.SET_CONFIG.value: self.set_config,
            SocketCommand.CONTROL.value: self.control,
            SocketCommand.UPGRADE.value: self.upgrade,
        }

    def set_callback(
        self,
        notify_warning,
        notify_status_change,
        notify_socket_picture,
        notify_socket_config,
    ) -> None:
        self.notify_warning_callback = notify_warning
        self.notify_socket_status_change_callback = notify_status_change
        self.notify_socket_picture_callback = notify_socket_picture
        self.notify_socket_config_callback = notify_socket_config

    def timerEvent(self, event):
        for timer, call in self.timerList:
            if event.timerId() == timer:
                call()

    @pyqtSlot()
    def run(self) -> None:
        self.control_signal.connect(self.handle_message)

        self.server = CameraServer()
        self.server.set_callback(self.notify_socket_picture_callback)
        self.serverQThread = create_and_start_thread(self.server)

        self.thread().exec()

        self.thread().quit()

    def deleteLater(self) -> None:
        for timer, _ in self.timerList:
            self.killTimer(timer)
        self.timerList.clear()

    def connect(self, ip, port) -> None:
        try:
            self.cameraSocket = DriverFactory.create(SOCKET_PRODUCT, ip, port)
            if self.cameraSocket is None:
                self.notify_warning_callback("摄像头连接失败")
                self.notify_socket_status_change_callback(False)
                return

            self.notify_socket_status_change_callback(True)
            self.server.set_camera_ip(ip)

            self.get_config()
        except Exception as e:
            self._handle_exception(e)

    def disconnect(self) -> None:
        try:
            if self.cameraSocket:
                self.cameraSocket.close()
                del self.cameraSocket
            self.cameraSocket = None
            self.server.set_camera_ip("")
            self.notify_socket_status_change_callback(False)
        except Exception as e:
            pass

    def get_config(self) -> None:
        try:
            config = self.cameraSocket.get_config()

            if config == "":
                self.notify_warning_callback("摄像头配置获取失败")
                return

            self.logger.info(f"摄像头配置: {config}")
            self.notify_socket_config_callback(config)
        except Exception as e:
            self._handle_exception(e)

    def set_config(self, config) -> None:
        try:
            if not self.cameraSocket.set_config(config):
                self.notify_warning_callback("摄像头配置失败")
        except Exception as e:
            self._handle_exception(e)

    def control(self, control_command) -> None:
        try:
            if not self.cameraSocket.control(control_command):
                self.notify_warning_callback("摄像头控制失败")
        except Exception as e:
            self._handle_exception(e)

    def upgrade(self, filePath) -> None:
        try:
            with open(filePath, "rb") as f:
                file = f.read()
                if not self.cameraSocket.upgrade(file):
                    self.notify_warning_callback("摄像头升级失败")
        except Exception as e:
            self._handle_exception(e)

    @pyqtSlot(str)
    def handle_message(self, message) -> None:
        try:
            messageDict = json.loads(message)
            command = messageDict.get("command")
            handler = self.command_handlers.get(command)

            if handler:
                if command in (
                    SocketCommand.DISCONNECT.value,
                    SocketCommand.GET_CONFIG.value,
                ):
                    handler()
                elif command in (
                    SocketCommand.SET_CONFIG.value,
                    SocketCommand.CONTROL.value,
                    SocketCommand.UPGRADE.value,
                ):
                    args_mapping = {
                        SocketCommand.SET_CONFIG.value: "config",
                        SocketCommand.CONTROL.value: "control",
                        SocketCommand.UPGRADE.value: "filePath",
                    }
                    arg_key = args_mapping.get(command)
                    if arg_key and arg_key in messageDict:
                        handler(messageDict[arg_key])
                    else:
                        self.logger.error(f"命令 '{command}' 缺少必需的参数。")
                elif command == SocketCommand.CONNECT.value:
                    if messageDict.get("ip") and messageDict.get("port"):
                        handler(messageDict["ip"], messageDict["port"])
                    else:
                        self.logger.error(f"命令 '{command}' 缺少必需的参数。")
                else:
                    self.logger.error(f"未定义参数处理逻辑的命令 '{command}'.")
            else:
                self.logger.error(f"收到未知命令: {command}")
        except json.JSONDecodeError:
            self.logger.error("接收到无效的JSON消息。")
        except Exception as e:
            self._handle_exception(e)

    def _handle_exception(self, exception) -> None:
        self.logger.error(f"发生错误: {exception}")
        if self.cameraSocket:
            self.cameraSocket.close()
            self.cameraSocket = None
        self.server.set_camera_ip("")
        self.notify_warning_callback(f"操作失败: {exception}")
        self.notify_socket_status_change_callback(False)
