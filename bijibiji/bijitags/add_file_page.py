import os
from typing import Set

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWizardPage, QHBoxLayout, QGroupBox, QVBoxLayout, \
    QPushButton, QListWidget, QListWidgetItem, QFileDialog

from .drop_area import DropArea
from .helpers import check_all, delete_from_list


# noinspection PyArgumentList,PyAttributeOutsideInit
class AddFilePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.button_max_width = 50
        self.files = set()

        self._init_ui_()

    def _init_ui_(self):
        self.setTitle("Add file")
        self.create_files_box()
        self.registerField('file_list*', self.fileList)

        drop_area = DropArea()
        drop_area.changed.connect(self.add_to_filelist)

        layout = QHBoxLayout()
        layout.addWidget(drop_area)
        layout.addWidget(self.filesBox)
        self.setLayout(layout)

    def create_files_box(self):
        self.filesBox = QGroupBox("Files")
        layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        self.all_files_button = QPushButton("All")
        self.all_files_button.setMaximumWidth(self.button_max_width)
        self.all_files_button.clicked.connect(lambda: check_all(self.fileList))
        self.delete_files_button = QPushButton("Del")
        self.delete_files_button.setMaximumWidth(self.button_max_width)
        self.delete_files_button.clicked.connect(self.delete_from_list)
        self.delete_files_button.setToolTip(
            "Delete checked items from the list")

        add_files_button = QPushButton("Add")
        add_files_button.setMaximumWidth(self.button_max_width)
        add_files_button.clicked.connect(self.add_files)

        buttons_layout.addWidget(self.all_files_button)
        buttons_layout.addWidget(self.delete_files_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_files_button)

        self.fileList = QListWidget()

        layout.addLayout(buttons_layout)
        layout.addWidget(self.fileList)
        self.filesBox.setLayout(layout)

    def add_files(self):
        files = QFileDialog.getOpenFileNames(
            parent=self,
            caption="Select one or more files",
            directory="."
        )
        files_set = set()
        for file in files[0]:
            files_set.add(os.path.relpath(file, start=os.getcwd()))
        self.add_to_filelist(files_set)

    def add_to_filelist(self, files: Set[str] = None):
        if files is None:
            return

        for file in files:
            if file.endswith('.biji.json') \
                    or self.fileList.findItems(file, Qt.MatchExactly):
                continue
            item = QListWidgetItem(self.fileList)
            item.setText(file)
            item.setCheckState(Qt.Unchecked)

        self.update_title()

        file_list = self.get_file_list()
        if file_list:
            """ Select the first row, enabling the Next-button. """
            self.fileList.setCurrentRow(0)
            self.files = set(file_list)

    def get_file_list(self):
        files = []
        for i in range(self.fileList.count()):
            files.append(self.fileList.item(i).text())
        return files

    def delete_from_list(self):
        delete_from_list(self.fileList)
        self.update_title()
        self.files = self.get_file_list()

    def update_title(self):
        self.filesBox.setTitle(f"Files - [{self.fileList.count()}]")
