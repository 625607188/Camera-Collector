from typing import Optional, Union
from src.driver.driver_serial.camera_serial.camera_serial import CameraSerial
from src.driver.driver_socket.camera_socket.camera_socket import CameraSocket


SERIAL_PRODUCT = "serial"
SOCKET_PRODUCT = "socket"


class DriverFactory:
    @staticmethod
    def create(product_type: str, *args) -> Optional[Union[CameraSerial, CameraSocket]]:
        if product_type == SERIAL_PRODUCT:
            product = CameraSerial()
        elif product_type == SOCKET_PRODUCT:
            product = CameraSocket()
        else:
            raise ValueError(f"Unsupported product type: {product_type}")

        if product.open(*args):
            return product
        return None
