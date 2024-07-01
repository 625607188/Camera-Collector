from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QStyle,
    QErrorMessage,
    QLabel,
    QCheckBox,
    QPushButton,
)


def Escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&#x27;")
    s = s.replace("\n", "<br/>")
    s = s.replace("  ", "&nbsp;")
    s = s.replace(" ", "&emsp;")
    return s


def showError(message, app) -> None:
    app.setQuitOnLastWindowClosed(True)
    # 设置内置错误图标
    window = QErrorMessage()
    window.setWindowIcon(
        app.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
    )
    window.finished.connect(lambda _: app.quit)
    window.resize(600, 400)
    # 去掉右上角?
    window.setWindowFlags(
        window.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
    )
    window.setWindowTitle(window.tr("Error"))
    # 隐藏图标、勾选框、按钮
    window.findChild(QLabel, "").setVisible(False)
    window.findChild(QCheckBox, "").setVisible(False)
    window.findChild(QPushButton, "").setVisible(False)
    window.showMessage(Escape(message))
    app.exec()
