import time
import pywifi
from PyQt6.QtCore import QObject, pyqtSlot
import logging


class WifiScanner(QObject):
    def __init__(self):
        super().__init__()

        logging.getLogger("pywifi").setLevel(logging.WARNING)
        logging.getLogger("comtypes").setLevel(logging.WARNING)

        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]

    def set_callback(self, notify_wifi_ssid) -> None:
        self.notify_wifi_ssid_callback = notify_wifi_ssid

    @pyqtSlot()
    def run(self):
        while True:
            self.iface.scan()
            time.sleep(1)

            results = self.iface.scan_results()

            ssidSet = set()
            for result in results:
                ssid_str = result.ssid.encode("raw_unicode_escape").decode("utf-8")

                if ssid_str:
                    ssidSet.add(ssid_str)

            self.notify_wifi_ssid_callback(sorted(list(ssidSet)))
            time.sleep(4)
