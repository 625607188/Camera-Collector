import socket
from src.driver.driver_socket.driver_socket import SocketBase
from src.driver.driver_socket.camera_socket.camera_socket_command import (
    get_camera_config,
    set_camera_config,
    control_camera,
    upgrade_camera,
)
from src.log import log

ERROR_SOCKET_SEND = "Socket send failed."
ERROR_SOCKET_RECV = "Socket receive failed."
ERROR_UNKNOWN = "An unknown error occurred."


class CameraSocket(SocketBase):
    def __init__(self) -> None:
        super().__init__()

        self.logger = log().get_logger()

    def _handle_error(self, error_msg):
        self.logger.error(error_msg)
        return False, ""

    def _send_command(self, command):
        try:
            if not self.send(command):
                return self._handle_error(ERROR_SOCKET_SEND)

            response = self.recv(1024)
            if response.startswith("HTTP/1.1 200 OK"):
                length = int(response.split("Content-Length: ")[1].split("\r\n")[0])
                if length > 0:
                    start_index = response.find("\r\n\r\n") + 4
                    payload = response[start_index : start_index + length]
                    return True, payload
                else:
                    return True, ""
            else:
                return self._handle_error("Unexpected response: " + response[:50])

        except socket.timeout:
            return self._handle_error(ERROR_SOCKET_RECV)
        except Exception as e:
            return self._handle_error(ERROR_UNKNOWN + f" Error details: {e}")

    def get_config(self):
        _, payload = self._send_command(get_camera_config())
        return payload

    def set_config(self, config):
        status, _ = self._send_command(set_camera_config(config))
        return status

    def control(self, command):
        status, _ = self._send_command(control_camera(command))
        return status

    def upgrade(self, file):
        status, _ = self._send_command(upgrade_camera(file))
        return status
