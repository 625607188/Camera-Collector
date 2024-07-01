import socket
from typing import Optional
from src.driver.driver_base import DriverBase


class SocketBase(DriverBase):
    def __init__(self) -> None:
        super(SocketBase, self).__init__()

        self.sock = None

    def open(self, ip, port) -> bool:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.0)
        try:
            self.sock.connect((ip, port))
            return True
        except Exception as e:
            self.logger.error("socket connect fail, %s", e)
            self.close()
            return False

    def close(self) -> None:
        del self.sock
        self.sock = None

    def send(self, s) -> bool:
        if not self.sock:
            return False

        try:
            self.sock.sendall(bytes(s, "utf-8"))
            return True
        except Exception as e:
            self.logger.error("send error, %s", e)
            return False

    def recv(self, size=1024) -> Optional[str]:
        if not self.sock:
            return None

        return str(self.sock.recv(size), "utf-8")
