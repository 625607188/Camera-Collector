import os
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtGui import QCloseEvent, QPixmap, QPainter, QColor, QImage
from src.common.thread.create_thread import create_and_start_thread
from src.driver.driver_serial.serial_base import get_serial_list
from src.log import log
from src.business.management.socket.socket_management import SocketManagement
from src.business.management.driver_management import DriverManagement
from src.ui.main_window_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    display_warning_signal = pyqtSignal(str)
    display_socket_status_change_signal = pyqtSignal(bool)
    display_socket_search_signal = pyqtSignal(list)
    display_socket_picture_signal = pyqtSignal(bytes)
    display_serial_list_signal = pyqtSignal(list)
    display_serial_status_change_signal = pyqtSignal(bool)
    display_wifi_ssid_signal = pyqtSignal(list)

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
            self.display_socket_search_signal,
            self.display_socket_picture_signal,
            self.display_serial_list_signal,
            self.display_serial_status_change_signal,
            self.display_wifi_ssid_signal,
        )

    def init_gui(self) -> None:
        width = self.label_pic.width()
        height = self.label_pic.height()
        blank_pixmap = QPixmap(width, height)
        blank_pixmap.fill(QColor(255, 255, 255))
        self.label_pic.setPixmap(blank_pixmap)

        self.comboBox_baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.comboBox_baud.setCurrentIndex(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        del self.driver_management

    def init_signals(self):
        self.display_warning_signal.connect(self.display_warning)
        self.display_socket_status_change_signal.connect(
            self.display_socket_status_change
        )
        self.display_socket_search_signal.connect(self.display_socket_search)
        self.display_socket_picture_signal.connect(self.display_socket_picture)
        self.display_serial_list_signal.connect(self.display_serial_list)
        self.display_wifi_ssid_signal.connect(self.display_wifi_ssid)

    def display_warning(self, warning) -> None:
        self.logger.warning(warning)
        QMessageBox.warning(self, "警告", warning)

    def display_socket_status_change(self, status) -> None:
        self.logger.info(status)
        self.checkBox_camera.setChecked(status)

        if status:
            self.lineEdit_filePath.setEnabled(True)
            self.pushButton_filePath.setEnabled(True)
        else:
            self.lineEdit_filePath.setEnabled(False)
            self.pushButton_filePath.setEnabled(False)
            self.pushButton_upgrade.setEnabled(False)

    def display_socket_search(self, result) -> None:
        currentText = (
            self.comboBox_camera.currentText()
            if self.checkBox_camera.isChecked()
            else ""
        )

        updatedResult = list(
            sorted(set(result + ([currentText] if currentText else [])))
        )

        if updatedResult != self.lastSocketResult:
            self.lastSocketResult = updatedResult

            self.comboBox_camera.clear()
            self.comboBox_camera.addItems(updatedResult)

            if self.checkBox_camera.isChecked():
                self.comboBox_camera.setCurrentText(currentText)
            else:
                self.comboBox_camera.setCurrentIndex(-1)

    @pyqtSlot()
    def update(self):
        if self.sender() == self.checkBox_serial:
            if self.checkBox_serial.isChecked():
                serial = self.comboBox_serial.currentText()
                baud = self.comboBox_baud.currentText()
                if serial and baud:
                    self.driver_management.serial_connect(serial, baud)
                else:
                    self.display_warning("请确认串口参数")
                    self.checkBox_serial.setChecked(False)
            else:
                self.driver_management.serial_disconnect()
                self.label_wifiStatus.setText("WiFi未连接")
                self.pushButton_connectWiFi.setEnabled(False)
                self.pushButton_disconnectWiFi.setEnabled(False)

        elif self.sender() == self.checkBox_camera:
            if self.checkBox_camera.isChecked():
                uuid = self.comboBox_camera.currentText()
                if uuid == "":
                    self.display_warning("请选择摄像头")
                    self.checkBox_camera.setChecked(False)
                    return

                self.driver_management.socket_connect(uuid)
            else:
                self.driver_management.socket_disconnect()

        elif self.sender() == self.lineEdit_filePath:
            if self.lineEdit_filePath.text():
                self.pushButton_upgrade.setEnabled(True)
            else:
                self.pushButton_upgrade.setEnabled(False)

        elif self.sender() == self.pushButton_filePath:
            print("pushButton_filePath")
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

    def display_serial_list(self, serial_list) -> None:
        currentText = self.comboBox_serial.currentText()

        self.comboBox_serial.clear()
        self.comboBox_serial.addItems(serial_list)
        if currentText in serial_list:
            self.comboBox_serial.setCurrentText(currentText)
        else:
            self.comboBox_serial.setCurrentIndex(-1)

    def display_serial_status_change(self, status) -> None:
        if not status:
            self.label_wifiStatus.setText("WiFi未连接")
            self.pushButton_connectWiFi.setEnabled(False)
            self.pushButton_disconnectWiFi.setEnabled(False)

    def display_wifi_ssid(self, ssid) -> None:
        currentText = self.comboBox_ssid.currentText()

        self.comboBox_ssid.clear()
        self.comboBox_ssid.addItems(ssid)
        if currentText in ssid:
            self.comboBox_ssid.setCurrentText(currentText)
        else:
            self.comboBox_ssid.setCurrentIndex(-1)
