from typing import Optional, Union
from src.driver.driver_socket.camera_socket.camera_socket import CameraSocket


SOCKET_PRODUCT = "socket"


class DriverFactory:
    @staticmethod
    def create(product_type: str, *args) -> Optional[Union[CameraSocket]]:
        if product_type == SOCKET_PRODUCT:
            product = CameraSocket()
        else:
            raise ValueError(f"Unsupported product type: {product_type}")

        if product.config(*args):
            return product
        return None
