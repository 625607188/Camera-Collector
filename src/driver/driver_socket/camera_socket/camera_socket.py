import socket
from src.driver.driver_socket.driver_socket import SocketBase
from src.driver.driver_socket.camera_socket.camera_socket_command import (
    ping_camera,
    get_camera_config,
    set_camera_config,
    control_camera,
    upgrade_camera,
)
from src.log import log

ERROR_SOCKET_OPEN = "Socket open failed."
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
            if not self.open():
                return self._handle_error(ERROR_SOCKET_OPEN)

            if not self.send(command):
                self.close()
                return self._handle_error(ERROR_SOCKET_SEND)

            response = ""
            while True:
                try:
                    trunk = self.recv(1024)
                    if len(trunk) == 0:
                        break
                    response = response + trunk
                except socket.timeout:
                    break

            if response.startswith("HTTP/1.1 200 OK"):
                length = int(response.split("Content-Length: ")[1].split("\r\n")[0])
                if length > 0:
                    start_index = response.find("\r\n\r\n") + 4
                    payload = response[start_index : start_index + length]
                    self.close()
                    return True, payload
                else:
                    self.close()
                    return True, ""
            else:
                self.close()
                return self._handle_error("Unexpected response: " + response[:50])

        except socket.timeout:
            self.close()
            return self._handle_error(ERROR_SOCKET_RECV)
        except Exception as e:
            self.close()
            return self._handle_error(ERROR_UNKNOWN + f" Error details: {e}")

    def ping(self):
        status, _ = self._send_command(ping_camera())
        return status

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
