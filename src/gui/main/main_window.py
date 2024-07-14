import json
import re
import os
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QRegularExpression
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import (
    QCloseEvent,
    QPixmap,
    QColor,
    QImage,
    QRegularExpressionValidator,
)
from src.log import log
from src.business.management.driver_management import DriverManagement
from src.ui.main_window_ui import Ui_MainWindow


def is_valid_ipv4(ip):
    pattern = re.compile(
        r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    return bool(pattern.match(ip))


def is_valid_port(port):
    return 0 <= int(port) <= 65535


class MainWindow(QMainWindow, Ui_MainWindow):
    display_warning_signal = pyqtSignal(str)
    display_socket_status_change_signal = pyqtSignal(bool)
    display_socket_search_signal = pyqtSignal(list)
    display_socket_picture_signal = pyqtSignal(bytes)
    display_socket_config_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.lastSerialResult = []
        self.lastSocketResult = []

        self.logger = log.get_logger()
        self.init_gui()

        self.init_signals()

        self.driver_management = DriverManagement(
            self,
            self.display_warning_signal,
            self.display_socket_status_change_signal,
            self.display_socket_picture_signal,
            self.display_socket_config_signal,
        )

    def init_gui(self) -> None:
        width = self.label_pic.width()
        height = self.label_pic.height()
        blank_pixmap = QPixmap(width, height)
        blank_pixmap.fill(QColor(255, 255, 255))
        self.label_pic.setPixmap(blank_pixmap)

        regVal = QRegularExpressionValidator()
        regVal.setRegularExpression(
            QRegularExpression(
                r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
                r":([0-9]|[1-9][0-9]{1,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"
            )
        )
        self.lineEdit_ipPort.setValidator(regVal)

    def closeEvent(self, event: QCloseEvent) -> None:
        del self.driver_management

    def init_signals(self):
        self.display_warning_signal.connect(self.display_warning)
        self.display_socket_status_change_signal.connect(
            self.display_socket_status_change
        )
        self.display_socket_picture_signal.connect(self.display_socket_picture)
        self.display_socket_config_signal.connect(self.display_socket_config)

    def display_warning(self, warning) -> None:
        self.logger.warning(warning)
        QMessageBox.warning(self, "警告", warning)

    def display_socket_status_change(self, status) -> None:
        self.logger.info(status)
        self.checkBox_camera.setChecked(status)

        if status:
            self.label_cameraStatus.setText("摄像头已连接")
            self.lineEdit_filePath.setEnabled(True)
            self.pushButton_filePath.setEnabled(True)
        else:
            self.label_cameraStatus.setText("摄像头未连接")
            self.lineEdit_filePath.setEnabled(False)
            self.pushButton_filePath.setEnabled(False)
            self.pushButton_upgrade.setEnabled(False)

    def _is_valid_json(self, json_str) -> bool:
        try:
            json.loads(json_str)
        except json.JSONDecodeError:
            return False
        return True

    @pyqtSlot()
    def update(self) -> None:
        if self.sender() == self.checkBox_camera:
            if self.checkBox_camera.isChecked():
                ipAndPort = self.lineEdit_ipPort.text()
                if ipAndPort == "":
                    self.display_warning("请确定ip和端口信息")
                    self.checkBox_camera.setChecked(False)
                    return

                ip, port = ipAndPort.split(":")
                # 校验ip和port是否正确
                if not is_valid_ipv4(ip) or not is_valid_port(port):
                    self.display_warning("ip和端口信息错误")
                    self.checkBox_camera.setChecked(False)
                    return

                self.label_cameraStatus.setText("摄像头连接中")
                self.driver_management.socket_connect(ip, int(port))
            else:
                self.driver_management.socket_disconnect()

        elif self.sender() == self.lineEdit_filePath:
            if self.lineEdit_filePath.text():
                self.pushButton_upgrade.setEnabled(True)
            else:
                self.pushButton_upgrade.setEnabled(False)

        elif self.sender() == self.pushButton_filePath:
            filePath = QFileDialog.getOpenFileName(
                self, "选择固件", "", "All Files (*)"
            )
            if filePath[0]:
                self.lineEdit_filePath.setText(filePath[0])

        elif self.sender() == self.pushButton_upgrade:
            filePath = self.lineEdit_filePath.text()
            if filePath and os.path.exists(filePath):
                self.driver_management.socket_upgrade(filePath)
            else:
                self.display_warning_signal.emit("固件路径错误")

        elif self.sender() == self.pushButton_refreshConfig:
            self.driver_management.socket_get_config()

        elif self.sender() == self.pushButton_config:
            config = self.textBrowser_config.toPlainText()
            if not self._is_valid_json(config):
                self.display_warning_signal.emit("配置了非法的json字符串")
                return

            self.driver_management.socket_set_config(
                json.dumps(json.loads(config), separators=(",", ":"))
            )

    def display_socket_picture(self, image) -> None:
        qimage = QImage()
        if qimage.loadFromData(image):
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(
                640,
                480,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.label_pic.setPixmap(scaled_pixmap)
        else:
            print("Failed to convert image data to QPixmap.")

    def display_socket_config(self, config):
        self.textBrowser_config.setText(json.dumps(json.loads(config), indent=4))
