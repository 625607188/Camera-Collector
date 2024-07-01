from http import client
import socket
from PyQt6.QtCore import QObject, pyqtSlot
from src.log import log

HTTP_OK = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"


class CameraServer(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.logger = log().get_logger()
        self.ip = "192.168.0.106"
        self.client_socket = None

    def set_callback(self, notify_socket_picture) -> None:
        self.notify_socket_picture_callback = notify_socket_picture

    def set_camera_ip(self, ip):
        self.ip = ip

        if not self.ip and self.client_socket is not None:
            try:
                self.client_socket.close()
                self.client_socket = None
            except OSError as e:
                print(f"Error occurred while closing socket: {e}")

    def listen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                server_socket.bind(("0.0.0.0", 10000))
                server_socket.listen()

                while True:
                    self.client_socket, addr = server_socket.accept()
                    self.logger.info(f"Accepted connection from {addr}")

                    with self.client_socket:
                        if addr[0] != self.ip:
                            self.logger.warn(f"abnormal ip {addr[0]}")
                            continue

                        self.client(self.client_socket)
                    self.client_socket = None
            except Exception as e:
                self.logger.error(f"Failed to start server: {e}")

    def client(self, sock):
        try:
            sock.settimeout(0.5)

            full_data = b""
            while True:
                try:
                    chunk = sock.recv(102400)
                    if not chunk:
                        break
                    full_data += chunk
                except socket.timeout:
                    break
                except Exception as e:
                    self.logger.error(f"Data receive error: {e}")
                    break

            if full_data:
                payload_start = full_data.find(b"\r\n\r\n") + 4
                if payload_start != -1:
                    head = full_data[:payload_start].decode("utf-8")
                    if head.startswith("POST /camera/image HTTP/1.1\r\n"):
                        content_length_header = "Content-Length: "
                        length_pos = head.find(content_length_header)
                        if length_pos != -1:
                            length_end = head.find("\r\n", length_pos)
                            if length_end != -1:
                                try:
                                    length = int(
                                        head[
                                            length_pos
                                            + len(content_length_header) : length_end
                                        ]
                                    )
                                    if (
                                        length > 0
                                        and len(full_data) >= payload_start + length
                                    ):
                                        payload = full_data[
                                            payload_start : payload_start + length
                                        ]
                                        self.notify_socket_picture_callback(payload)
                                    else:
                                        self.logger.warning(
                                            "Invalid content length or data size."
                                        )
                                except ValueError:
                                    self.logger.error("Failed to parse Content-Length.")
                            else:
                                self.logger.warning(
                                    "Incomplete header: missing end of line after Content-Length."
                                )
                        else:
                            self.logger.warning(
                                "Header does not contain Content-Length."
                            )
                    else:
                        self.logger.warning(
                            f"Unexpected request format: {head[:50]}..."
                        )
                else:
                    self.logger.warning("Payload start marker not found.")
            else:
                self.logger.info("No data received.")

            sock.sendall(HTTP_OK)
        except Exception as e:
            self.logger.error(f"Critical error in client handling: {e}")

    @pyqtSlot()
    def run(self):
        self.listen()
