from src.log import log
from src.driver.driver_serial.serial_base import SerialBase
from src.driver.driver_serial.camera_serial.camera_serial_command import (
    parse_read_ack,
    parse_write_ack,
    get_ssid_command,
    set_ssid_command,
    get_password_command,
    set_password_command,
    get_wifi_enable_command,
    set_wifi_enable_command,
    get_wifi_connect_status_command,
)


class CameraSerial(SerialBase):
    def __init__(self) -> None:
        super().__init__()
        self.logger = log.get_logger()

    def get_ssid(self) -> str:
        try:
            self.send(get_ssid_command())
            data = parse_read_ack(self.recv(100))
            if data == []:
                self.logger.warning("get ssid error")
                return ""
            return str(data)

        except Exception as e:
            self.logger.error(e)

        return ""

    def set_ssid(self, ssid: str) -> None:
        try:
            self.send(set_ssid_command(ssid))
            if parse_write_ack(self.recv(100)) is False:
                self.logger.warning("set ssid error")
                return
        except Exception as e:
            self.logger.error(e)

    def get_password(self) -> str:
        try:
            self.send(get_password_command())
            data = parse_read_ack(self.recv(100))
            if data == []:
                self.logger.warning("get password error")
                return ""
            return str(data)

        except Exception as e:
            self.logger.error(e)

        return ""

    def set_password(self, password: str) -> None:
        try:
            self.send(set_password_command(password))
            if parse_write_ack(self.recv(100)) is False:
                self.logger.warning("set password error")
                return
        except Exception as e:
            self.logger.error(e)

    def get_wifi_enable(self) -> None:
        try:
            self.send(get_wifi_enable_command())
            if parse_read_ack(self.recv(100)) is False:
                self.logger.warning("get wifi enable error")
                return
        except Exception as e:
            self.logger.error(e)

    def set_wifi_enable(self) -> None:
        try:
            self.send(set_wifi_enable_command())
            if parse_write_ack(self.recv(100)) is False:
                self.logger.warning("set wifi enable error")
                return
        except Exception as e:
            self.logger.error(e)

    def get_wifi_connect_status(self) -> None:
        try:
            self.send(get_wifi_connect_status_command())
            if parse_read_ack(self.recv(100)) is False:
                self.logger.warning("get wifi status error")
                return
        except Exception as e:
            self.logger.error(e)
