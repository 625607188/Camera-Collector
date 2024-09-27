from http import client
import socket
from PyQt6.QtCore import QObject, pyqtSlot
from src.log import log

HTTP_OK = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
HTTP_NOTOK = b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n"


class CameraServer(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.logger = log().get_logger()
        self.ip = ""
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
            sock.settimeout(1.0)

            full_data = b""
            head = ""
            content_length = 0

            while True:
                try:
                    chunk = sock.recv(512)
                    if len(chunk) == 0:
                        self.logger.warn(f"recv no data.")
                        break
                    full_data += chunk
                    if b"\r\n\r\n" in full_data:
                        break

                except socket.timeout:
                    self.logger.warn("recv timeout.")
                    break
                except Exception as e:
                    self.logger.error(f"Data receive error: {e}")
                    break

            if len(full_data) == 0:
                self.logger.error("recv no data.")
                sock.sendall(HTTP_NOTOK)
                return

            payload_start = full_data.find(b"\r\n\r\n") + 4
            if payload_start == -1:
                self.logger.error(f"recv no head for {len(full_data)} data.")
                sock.sendall(HTTP_NOTOK)
                return

            head = full_data[:payload_start].decode("utf-8")
            if not head.startswith("POST /camera/image HTTP/1.1\r\n"):
                self.logger.error(f"recv head error, {full_data[:20]}")
                sock.sendall(HTTP_NOTOK)
                return

            content_length_header = "Content-Length: "
            length_pos = head.find(content_length_header)
            if length_pos != -1:
                length_end = head.find("\r\n", length_pos)
                if length_end != -1:
                    try:
                        content_length = int(
                            head[length_pos + len(content_length_header) : length_end]
                        )
                    except ValueError:
                        self.logger.error("Failed to parse Content-Length.")
                        sock.sendall(HTTP_NOTOK)
                        return

            if content_length <= 0:
                self.logger.error(f"Parse Content-Length error, {content_length}.")
                sock.sendall(HTTP_NOTOK)
                return

            remaining_length = content_length - (len(full_data) + -len(head))
            while remaining_length > 0:
                try:
                    chunk = sock.recv(min(remaining_length, 32768))
                    if len(chunk) == 0:
                        self.logger.warn(
                            f"waiting for {min(remaining_length, 32768)} data."
                        )
                        self.logger.warn(f"recv no data.")
                        break
                    full_data += chunk
                    remaining_length -= len(chunk)
                except socket.timeout:
                    self.logger.error(f"recv timeout.")
                    break
                except Exception as e:
                    self.logger.error(f"Data receive error: {e}")
                    break

            self.logger.info(
                f"data {len(full_data)}, head: {len(head)}, length: {content_length}."
            )

            if len(full_data) != len(head) + content_length:
                self.logger.error(
                    f"Invalid content length or data size, data {len(full_data)}, head: {len(head)}, length: {content_length}."
                )
                sock.sendall(HTTP_NOTOK)
                return

            payload = full_data[payload_start:]
            image_start = payload.find(b"\r\n\r\n") + 4
            image_end = payload[image_start:-2].rfind(b"\r\n")

            image = payload[image_start : image_start + image_end]

            self.notify_socket_picture_callback(image)

            sock.sendall(HTTP_OK)

        except Exception as e:
            self.logger.error(f"Critical error in client handling: {e}")

    @pyqtSlot()
    def run(self):
        self.listen()
