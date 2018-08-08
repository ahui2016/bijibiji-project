from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGroupBox, QListWidget, QLabel, QFrame, \
    QListWidgetItem, QVBoxLayout

from ..bijidb.bijidatabase import BijiDatabase


# noinspection PyArgumentList
class FileInfoBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = BijiDatabase
        self.preview_width = 200
        self.preview_margin = 50

        self.setTitle('File info')
        self.file_tag_list = QListWidget()
        self.file_tag_list.setFixedWidth(
            self.preview_width + self.preview_margin)

        self.file_preview = QLabel('Preview')
        self.file_preview.setFixedSize(
            self.preview_width + self.preview_margin,
            self.preview_width + self.preview_margin)
        self.file_preview.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.file_preview.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.file_preview)
        layout.addWidget(self.file_tag_list)
        self.setLayout(layout)
        self.setFixedWidth(self.preview_width + self.preview_margin + 20)

    def update_file_info(self, item: Optional[QListWidgetItem]) -> None:
        self.file_tag_list.clear()
        if item is None:
            self.file_preview.setText('Preview')
            return

        file = item.text()
        preview = QPixmap(file)
        if preview.isNull():
            self.file_preview.setText(f'{file}')
        else:
            thumb = preview.scaled(
                self.preview_width, self.preview_width, Qt.KeepAspectRatio)
            self.file_preview.setPixmap(thumb)

        for tag in self.db.get_tags(file):
            item = QListWidgetItem(self.file_tag_list)
            item.setText(tag)
