import socket
import json
import time
from PyQt6.QtCore import Qt, QObject, QTimerEvent, pyqtSlot
from src.log import log


class SocketInfo(QObject):
    def __init__(self, ip, port, uuid) -> None:
        self.ip = ip
        self.port = port
        self.uuid = uuid
        self.timestamp = time.time()

    def get_uuid(self):
        return self.uuid

    def get_ip_port(self):
        return f"{self.ip}:{self.port}"


class SearchSocket(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.logger = log.get_logger()
        self.timerList = []
        self.sockets = []

    def set_callback(
        self,
        notify_socket_search,
    ) -> None:
        self.notify_socket_search_callback = notify_socket_search

    def join_multicast(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", 5000))
        self.sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton("224.0.0.1") + socket.inet_aton("0.0.0.0"),
        )
        self.sock.settimeout(0.1)

    def remove_duplicates(self, new_socket_info: SocketInfo) -> None:
        self.sockets = [
            sock for sock in self.sockets if sock.uuid != new_socket_info.uuid
        ]

    def filter_inactive_sockets(self, current_time: float) -> None:
        self.sockets = [
            sock for sock in self.sockets if sock.timestamp + 20 >= current_time
        ]

    def sort_sockets_by_ip(self) -> None:
        self.sockets.sort(key=lambda x: x.uuid)

    def recv_message(self) -> None:
        try:
            data = self.sock.recv(1024)
            info = json.loads(data.decode())
            new_socket_info = SocketInfo(info["ip"], info["port"], info["uuid"])

            self.remove_duplicates(new_socket_info)
            self.sockets.append(new_socket_info)
            self.logger.info(
                f"find socket: {new_socket_info.ip}:{new_socket_info.port}, {new_socket_info.uuid}"
            )

        except socket.timeout:
            pass

        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from received data.")

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

        current_time = time.time()
        self.filter_inactive_sockets(current_time)
        self.sort_sockets_by_ip()

        if len(self.sockets) > 0:
            self.notify_socket_search_callback(self.sockets[0].get_ip_port())

    def timerEvent(self, event: QTimerEvent):
        for timer, call in self.timerList:
            if event.timerId() == timer:
                call()

    @pyqtSlot()
    def run(self):
        self.join_multicast()

        self.find_socket = self.startTimer(200, Qt.TimerType.PreciseTimer)
        self.timerList.append((self.find_socket, lambda: self.recv_message()))

        self.thread().exec()

        self.thread().quit()

    def deleteLater(self):
        for timer, _ in self.timerList:
            self.killTimer(timer)
        self.timerList.clear()

    def find_socket_info(self, uuid: str):
        for socket in self.sockets:
            if socket.uuid == uuid:
                return socket
        return None
