import os
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDropEvent, QPalette
from PyQt5.QtWidgets import QLabel, QFrame, QMessageBox


# noinspection PyCallByClass,PyArgumentList
class DropArea(QLabel):

    changed = pyqtSignal([list])

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(200, 200)
        self.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        self.setText("<drop here>")
        self.setBackgroundRole(QPalette.Dark)

    def dragEnterEvent(self, event: QDropEvent):
        self.setBackgroundRole(QPalette.Highlight)
        event.acceptProposedAction()
        self.setText("<drop here>")

    def dragMoveEvent(self, event: QDropEvent):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = []
            for url in mime_data.urls():
                file_path = Path(url.toLocalFile())
                if not file_path.is_file():
                    continue
                try:
                    relative_path = file_path.relative_to(os.getcwd())
                    urls.append(str(relative_path))
                except ValueError:
                    QMessageBox.information(
                        self, "Out of scope",
                        "Can not add file which is outside of bijibiji's "
                        "home.\n",
                        QMessageBox.Close)
                    break
            if urls:
                self.changed.emit(urls)
        else:
            self.setText("<Not File>\n"
                         "<drop file(s) here>")

        self.setBackgroundRole(QPalette.Dark)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        event.accept()

    # def clear(self):
    #     self.setText("<drop here>")
    #     self.setBackgroundRole(QPalette.Dark)
