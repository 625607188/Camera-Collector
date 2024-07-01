from PyQt6.QtCore import QObject, QThread


def create_and_start_thread(thread: QObject) -> QThread:
    qThread = QThread()

    thread.moveToThread(qThread)
    qThread.started.connect(thread.run)
    qThread.finished.connect(thread.deleteLater)

    qThread.start()

    return qThread
