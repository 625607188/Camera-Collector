import sys
import traceback
from PyQt6.QtWidgets import QApplication

from src.errorDisplay import showError
from src.gui.main.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        showError(traceback.format_exc(), app)
        sys.exit(-111)
