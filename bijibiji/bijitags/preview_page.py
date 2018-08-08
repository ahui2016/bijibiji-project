from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWizardPage, QListWidgetItem, QGroupBox, \
    QVBoxLayout, QListWidget, QHBoxLayout, QWizard, QLabel, QMessageBox

from .biji import Biji


# noinspection PyArgumentList,PyAttributeOutsideInit,PyCallByClass
# PyUnresolvedReferences
class PreviewPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.files = set()
        self.old_common_tags = set()
        self.new_common_tags = set()
        self.create_files_box()
        self.create_deleted_tags_box()
        self.create_new_tags_box()

        self._init_ui_()

    def _init_ui_(self):
        self.setTitle("Preview")
        self.setButtonText(QWizard.NextButton, "Apply")

        layout = QHBoxLayout()
        layout.addWidget(self.filesBox)
        layout.addWidget(self.deletedTagsBox)
        layout.addWidget(self.newTagsBox)
        self.setLayout(layout)

        self.label = QLabel("Nothing's changed.\n")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.hide()
        layout.addWidget(self.label)

    def initializePage(self):
        self.deleted_tags = self.old_common_tags - self.new_common_tags
        self.new_added_tags = self.new_common_tags - self.old_common_tags

        if not self.deleted_tags.union(self.new_added_tags):
            self.filesBox.hide()
            self.deletedTagsBox.hide()
            self.newTagsBox.hide()
            self.label.show()
            return
        else:
            self.setSubTitle("")
            self.filesBox.show()
            self.deletedTagsBox.show()
            self.newTagsBox.show()
            self.label.hide()

        self.fileList.clear()
        self.deletedTagsList.clear()
        self.newTagsList.clear()

        for file in self.files:
            item = QListWidgetItem(self.fileList)
            item.setText(file)
            # item.setFlags(Qt.NoItemFlags)

        for tag in self.deleted_tags:
            item = QListWidgetItem(self.deletedTagsList)
            item.setText(tag)

        for tag in self.new_added_tags:
            item = QListWidgetItem(self.newTagsList)
            item.setText(tag)

    def isComplete(self):
        return self.label.isHidden()

    def validatePage(self):
        answer = QMessageBox.question(self, "Apply", "Apply changes to files?",
                                      defaultButton=QMessageBox.No)
        if answer == QMessageBox.No:
            return False

        Biji.update_tags_for_files(self.files,
                                   self.deleted_tags,
                                   self.new_added_tags)
        return True

    def create_files_box(self):
        self.filesBox = QGroupBox("Files")
        layout = QVBoxLayout()
        self.fileList = QListWidget()
        layout.addWidget(self.fileList)
        self.filesBox.setLayout(layout)

    def create_deleted_tags_box(self):
        self.deletedTagsBox = QGroupBox("Deleted tags")
        layout = QVBoxLayout()
        self.deletedTagsList = QListWidget()
        layout.addWidget(self.deletedTagsList)
        self.deletedTagsBox.setLayout(layout)

    def create_new_tags_box(self):
        self.newTagsBox = QGroupBox("New added tags")
        layout = QVBoxLayout()
        self.newTagsList = QListWidget()
        layout.addWidget(self.newTagsList)
        self.newTagsBox.setLayout(layout)
