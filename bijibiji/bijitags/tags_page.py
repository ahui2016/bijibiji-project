from typing import List

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWizard, QWizardPage, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, \
    QInputDialog, QMessageBox

from .biji import Biji
from .helpers import check_all, delete_from_list
from ..bijidb.bijidatabase import BijiDatabase
from .file_info_box import FileInfoBox


# noinspection PyArgumentList,PyAttributeOutsideInit,PyCallByClass
# noinspection PyUnresolvedReferences
class TagsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.files = set()
        self.old_files = set()
        self.new_common_tags = set()
        self.recently_deleted_tags = set()
        self.button_max_width = 50
        self.box_mini_width = 225
        self.create_files_box()
        self.create_common_tags_box()
        self.create_recommended_tags_box()
        self.create_all_tags_box()
        self.file_info_box = FileInfoBox()

        self._init_ui_()

    def _init_ui_(self) -> None:
        self.setTitle("Tags")
        self.setButtonText(QWizard.NextButton, "Preview")

        layout = QHBoxLayout()
        layout.addWidget(self.filesBox)
        layout.addWidget(self.file_info_box)

        tags_layout = QVBoxLayout()
        tags_layout.addWidget(self.commonTagsBox)
        tags_layout.addWidget(self.recommendTagsBox)
        layout.addLayout(tags_layout)

        layout.addWidget(self.allTagsBox)
        self.setLayout(layout)

    def initializePage(self):
        if self.old_files == self.files:
            return
        else:
            self.old_files = self.files

        self.fileList.clear()
        self.tagList.clear()
        self.recommendTagsList.clear()
        self.new_common_tags.clear()
        self.allTagsList.clear()

        for file in self.files:
            item = QListWidgetItem(self.fileList)
            item.setText(file)
            # item.setFlags(Qt.NoItemFlags)

        tag_set_list: List[set] = []
        for file in self.files:
            if Biji.get_biji_json_path(file).exists():
                biji = Biji.from_file(file)
                tag_set_list.append(set(biji.tags))
            else:
                tag_set_list.append(set())

        if tag_set_list:
            self.common_tags = tag_set_list[0].intersection(*tag_set_list[1:])
            all_tags = tag_set_list[0].union(*tag_set_list[1:])
        else:
            self.common_tags = set()
            all_tags = set()

        if self.common_tags:
            for tag in self.common_tags:
                item = QListWidgetItem(self.tagList)
                item.setText(tag)
                item.setCheckState(Qt.Unchecked)
                item.setFlags(item.flags() | Qt.ItemIsEditable)

        recommend_tags = all_tags - self.common_tags
        if recommend_tags:
            for tag in recommend_tags:
                item = QListWidgetItem(self.recommendTagsList)
                item.setText(tag)

        recently_deleted_tags = \
            self.recently_deleted_tags - recommend_tags - self.common_tags
        self.recommendTagsList.insertItems(0, recently_deleted_tags)

        for row in BijiDatabase.get_all_tags_desc():
            item = QListWidgetItem(self.allTagsList)
            item.setText(row['tag'])

        self.fileList.setCurrentRow(0)

    def validatePage(self):
        self.update_new_common_tags()
        return True

    def cleanupPage(self):
        self.update_new_common_tags()
        new_added_tags = self.new_common_tags - self.common_tags
        self.recently_deleted_tags |= new_added_tags

    def update_new_common_tags(self) -> None:
        self.new_common_tags.clear()
        for i in range(self.tagList.count()):
            self.new_common_tags.add(self.tagList.item(i).text().strip())

    def create_files_box(self) -> None:
        self.filesBox = QGroupBox("Files")
        self.filesBox.setMinimumWidth(self.box_mini_width)
        layout = QVBoxLayout()

        self.fileList = QListWidget()
        self.fileList.currentItemChanged.connect(self.update_file_info)

        layout.addWidget(self.fileList)
        self.filesBox.setLayout(layout)

    def create_common_tags_box(self) -> None:
        self.commonTagsBox = QGroupBox("Common Tags")
        self.commonTagsBox.setMinimumWidth(self.box_mini_width)
        layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        all_tags_button = QPushButton("All")
        all_tags_button.setMaximumWidth(self.button_max_width)
        all_tags_button.clicked.connect(lambda: check_all(self.tagList))
        delete_tags_button = QPushButton("Del")
        delete_tags_button.setMaximumWidth(self.button_max_width)
        delete_tags_button.clicked.connect(self.delete_tags)
        delete_tags_button.setToolTip("Delete checked items from the list")

        add_tags_button = QPushButton("Add")
        add_tags_button.setMaximumWidth(self.button_max_width)
        add_tags_button.clicked.connect(self.add_tags)

        buttons_layout.addWidget(all_tags_button)
        buttons_layout.addWidget(delete_tags_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_tags_button)

        self.tagList = QListWidget()

        layout.addLayout(buttons_layout)
        layout.addWidget(self.tagList)
        self.commonTagsBox.setLayout(layout)

    def create_recommended_tags_box(self) -> None:
        self.recommendTagsBox = QGroupBox("Recommended Tags")
        self.recommendTagsBox.setMinimumWidth(self.box_mini_width)
        layout = QVBoxLayout()
        self.recommendTagsList = QListWidget()
        layout.addWidget(self.recommendTagsList)
        self.recommendTagsBox.setLayout(layout)

        self.recommendTagsList.doubleClicked.connect(self.move_to_common_tags)

    def create_all_tags_box(self) -> None:
        self.allTagsBox = QGroupBox("All Tags")
        self.allTagsBox.setMinimumWidth(self.box_mini_width)
        layout = QVBoxLayout()
        self.allTagsList = QListWidget()
        layout.addWidget(self.allTagsList)
        self.allTagsBox.setLayout(layout)

        self.allTagsList.doubleClicked.connect(self.copy_to_common_tags)

    def delete_tags(self) -> None:
        deleted_items = delete_from_list(self.tagList)
        self.recently_deleted_tags |= deleted_items

        for item in deleted_items:
            if not self.recommendTagsList.findItems(item, Qt.MatchExactly):
                self.recommendTagsList.insertItem(0, item)

    def add_tags(self) -> None:
        tag, ok = QInputDialog.getText(self, "New tag", "New tag:")
        tag = tag.strip()
        if not ok or len(tag) == 0:
            return
        if self.tagList.findItems(
                tag, Qt.MatchFixedString | Qt.MatchCaseSensitive):
            QMessageBox.information(self, "Duplicated.",
                                    "The tag is already in the list.\n",
                                    QMessageBox.Close)
            return
        item = QListWidgetItem(self.tagList)
        item.setText(tag)
        item.setCheckState(Qt.Unchecked)
        item.setFlags(item.flags() | Qt.ItemIsEditable)

    def copy_to_common_tags(self, index: QModelIndex) -> None:
        if not self.tagList.findItems(
                index.data(), Qt.MatchFixedString | Qt.MatchCaseSensitive):
            item = QListWidgetItem(self.tagList)
            item.setText(index.data())
            item.setCheckState(Qt.Unchecked)
            item.setFlags(item.flags() | Qt.ItemIsEditable)

    def move_to_common_tags(self, index: QModelIndex) -> None:
        self.copy_to_common_tags(index)
        self.recommendTagsList.takeItem(index.row())

    def update_file_info(self, current: QListWidgetItem) -> None:
        self.file_info_box.update_file_info(current)
