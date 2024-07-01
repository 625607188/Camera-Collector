from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal

from src.log import log


class DriverInfo(QObject):
    robot_status_change_signal = pyqtSignal(bool)
    robot_tool_user_signal = pyqtSignal(int, int)
    robot_current_pose_signal = pyqtSignal(float, float, float)
    incubator_status_change_signal = pyqtSignal(bool)
    incubator_data_signal = pyqtSignal(float, float)
    force_status_change_signal = pyqtSignal(bool)
    force_data_list_signal = pyqtSignal(list)

    def __init__(self, parent=None) -> None:
        super(DriverInfo, self).__init__(parent)

        self.logger = log.get_logger()
        self.robot_status = False
        self.incubator_status = False
        self.force_status = False
        self.ip = ""
        self.port = 0
        self.incubator_com = ""
        self.incubator_config = 0, 0
        self.force_com = ""
        self.force_config = 0

    def update_robot_connect_info(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

    def get_robot_connect_info(self) -> tuple[str, int]:
        return self.ip, self.port

    def get_robot_status_change_signal(self) -> pyqtBoundSignal:
        return self.robot_status_change_signal

    def get_robot_status(self) -> bool:
        return self.robot_status

    def update_robot_status(self, status: bool) -> None:
        self.robot_status = status
        self.robot_status_change_signal.emit(status)
        self.logger.info(f"robot status: {status}")

    def get_robot_tool_user_signal(self) -> pyqtBoundSignal:
        return self.robot_tool_user_signal

    def get_robot_tool_user_number(self):
        return self.tool_number, self.user_number

    def update_robot_tool_user_number(self, tool, user) -> None:
        self.tool_number = tool
        self.user_number = user
        self.robot_tool_user_signal.emit(tool, user)

    def get_robot_current_pose_signal(self) -> pyqtBoundSignal:
        return self.robot_current_pose_signal

    def update_robot_current_pose(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.robot_current_pose_signal.emit(x, y, z)

    def update_incubator_connect_info(self, com: str) -> None:
        self.incubator_com = com

    def get_incubator_connect_info(self) -> str:
        return self.incubator_com

    def get_incubator_status_change_signal(self) -> pyqtBoundSignal:
        return self.incubator_status_change_signal

    def get_incubator_status(self) -> bool:
        return self.incubator_status

    def update_incubator_status(self, status: bool) -> None:
        self.incubator_status = status
        self.incubator_status_change_signal.emit(status)
        self.logger.info(f"incubator status: {status}")

    def get_incubator_data_signal(self) -> pyqtBoundSignal:
        return self.incubator_data_signal

    def update_incubator_data(self, temp, humidity) -> None:
        self.incubator_data_signal.emit(temp, humidity)

    def update_incubator_config(self, temp, humidity) -> None:
        self.incubator_config = temp, humidity

    def get_incubator_config(self) -> tuple[float, float]:
        return self.incubator_config

    def update_force_connect_info(self, com: str) -> None:
        self.force_com = com

    def get_force_connect_info(self) -> str:
        return self.force_com

    def get_force_status_change_signal(self) -> pyqtBoundSignal:
        return self.force_status_change_signal

    def get_force_status(self) -> bool:
        return self.force_status

    def update_force_status(self, status: bool) -> None:
        self.force_status = status
        self.force_status_change_signal.emit(status)
        self.logger.info(f"force status: {status}")

    def get_force_data_list_signal(self) -> pyqtBoundSignal:
        return self.force_data_list_signal

    def update_force_data_list(self, data_list) -> None:
        self.force_data_list_signal.emit(data_list)

    def update_force_config(self, force) -> None:
        self.force_config = force

    def get_force_config(self) -> int:
        return self.force_config
