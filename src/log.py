import logging
from src.common.designPattern.singleton import SingletonBase

log_path = r"log.txt"


# 单例模式
class log(SingletonBase):
    def __init__(self) -> None:
        if not hasattr(self, "logger"):
            l = logging.getLogger()
            l.setLevel(level=logging.DEBUG)
            filehandle = logging.FileHandler(log_path, encoding="utf-8")
            streamhandle = logging.StreamHandler()
            l.addHandler(filehandle)
            l.addHandler(streamhandle)
            formatter = logging.Formatter(
                "%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s %(message)s"
            )
            filehandle.setFormatter(formatter)
            streamhandle.setFormatter(formatter)

            self.logger = l

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return log().logger


if __name__ == "__main__":
    logger = log.get_logger()
    logger.debug("Hello, world")
