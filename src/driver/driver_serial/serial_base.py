from typing import Optional, Dict
from serial import Serial
from serial.tools.list_ports import comports
from crcmod.predefined import mkPredefinedCrcFun
from src.driver.driver_base import DriverBase


def generate_crc(commandList) -> list:
    crc16 = mkPredefinedCrcFun("modbus")
    calculatedCrc = crc16(bytes(commandList))

    crcList = [(calculatedCrc & 0xFF), (calculatedCrc >> 8) & 0xFF]
    return crcList


def get_serial_list() -> Dict:
    serials = {}
    ports = comports()
    for port, desc, _ in ports:
        if "蓝牙" in desc:
            continue
        serials[port] = desc
    return serials


class SerialBase(DriverBase):
    def __init__(self) -> None:
        super(SerialBase, self).__init__()

        self.serials = {}
        self.serialFd = None

    def __del__(self) -> None:
        self.close()

    def open(self, serialName, baudrate, bytesize=8, stopbits=1, timeout=0.5) -> bool:
        try:
            self.serialFd = Serial(
                port=serialName,
                baudrate=baudrate,
                bytesize=bytesize,
                stopbits=stopbits,
                timeout=timeout,
            )
            return True
        except Exception as e:
            self.logger.debug("open forceSensor serial fail! %s", e)
            self.serialFd = None
            return False

    def close(self) -> None:
        if self.serialFd:
            del self.serialFd
            self.serialFd = None

    def send(self, s) -> bool:
        if not self.serialFd:
            return False

        try:
            self.serialFd.reset_input_buffer()
            self.serialFd.reset_output_buffer()
            return len(s) == self.serialFd.write(s)
        except Exception as e:
            self.logger.debug("write forceSensor serial fail! %s", e)

        return False

    def recv(self, size=1024) -> Optional[bytes]:
        if not self.serialFd:
            return None

        try:
            return self.serialFd.read(size)
        except Exception as e:
            self.logger.warning("read forceSensor serial fail! %s", e)

        return None
