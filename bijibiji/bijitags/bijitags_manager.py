from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QListWidget, \
    QListWidgetItem, QApplication, QVBoxLayout, QComboBox, QPushButton, \
    QMessageBox, QGroupBox, QInputDialog, qApp, QLabel, QFrame

from ..bijitags.biji import Biji
from ..bijitags.helpers import get_checked_items
from ..bijidb.bijidatabase import BijiDatabase
from ..bijiscan.bijiscanner import biji_json_not_exists
from .file_info_box import FileInfoBox


# noinspection PyArgumentList,PyUnresolvedReferences,PyCallByClass
class BijitagsManager(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = BijiDatabase
        try:
            self.db.connect_db()
        except FileNotFoundError:
            BijiDatabase.create_db()
            QMessageBox.information(
                self,
                "Error",
                "[Database not found]\n"
                "Please run scan_all_and_update or bijitags_wizard first.\n",
                QMessageBox.Close)
            self.close()
            qApp.quit()
            QApplication.instance().quit()
            sys.exit(1)

        self.preview_height = 200

        if biji_json_not_exists(self.db):
            QMessageBox.information(
                self,
                "FileNotFoundError",
                "[FileNotFoundError]\n"
                "Please run bijibiji.bijiscan.bijiscan_gui to get "
                "more information.\n",
                QMessageBox.Close)
            self.db.close_db()
            self.close()
            qApp.quit()
            QApplication.instance().quit()
            sys.exit(1)

        self.tags_by_count = None
        self.tags_by_time = None
        self.tags_by_alphabet = None

        self.tag_list_by_count = QListWidget()
        self.tag_list_by_count.doubleClicked.connect(self.edit_tag)
        self.tag_list_by_count.currentItemChanged.connect(
            self.update_file_list)

        self.tag_list_by_time = QListWidget()
        self.tag_list_by_time.setVisible(False)
        self.tag_list_by_time.doubleClicked.connect(self.edit_tag)
        self.tag_list_by_time.currentItemChanged.connect(
            self.update_file_list)

        self.tag_list_by_alphabet = QListWidget()
        self.tag_list_by_alphabet.setVisible(False)
        self.tag_list_by_alphabet.doubleClicked.connect(self.edit_tag)
        self.tag_list_by_alphabet.currentItemChanged.connect(
            self.update_file_list)

        self.files_box = QGroupBox('Files')
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.update_file_info)

        self.file_info_box = FileInfoBox()

        self.file_preview = QLabel('Preview')
        self.file_preview.setFixedSize(self.preview_height + 50,
                                       self.preview_height + 50)
        self.file_preview.setFrameStyle(QFrame.Sunken | QFrame.StyledPanel)
        self.file_preview.setAlignment(Qt.AlignCenter)

        self.update_all_tag_lists()
        self.current_tag_list = self.tag_list_by_count

        self._init_ui_()

    def _init_ui_(self) -> None:
        self.setWindowTitle('Tags Manager - bijibiji')
        self.setBackgroundRole(QPalette.Dark)
        self.setAutoFillBackground(True)
        self.create_central_widget()

    def closeEvent(self, event):
        self.db.close_db()
        event.accept()

    @staticmethod
    def generate_new_tags(old_tags: set, deleted: set, added: set) -> set:
        return old_tags - deleted | added

    @staticmethod
    def update_tag_list(tags, tag_list: QListWidget) -> None:
        tag_list.clear()
        for row in tags:
            item = QListWidgetItem(tag_list)
            item.setData(Qt.UserRole, row[0])
            if type(tags) is list:
                item.setText(f"({row[1]}) {row[0]}")
            else:
                item.setText(row['tag'])
            item.setCheckState(Qt.Unchecked)

    def update_all_tag_lists(self) -> None:
        self.tags_by_count = self.db.get_tags_order_by_count()
        self.update_tag_list(self.tags_by_count, self.tag_list_by_count)
        self.tags_by_time = self.db.get_tags_order_by_time()
        self.update_tag_list(self.tags_by_time, self.tag_list_by_time)
        self.tags_by_alphabet = self.db.get_tags_order_by_tag()
        self.update_tag_list(self.tags_by_alphabet, self.tag_list_by_alphabet)

    # noinspection PyUnresolvedReferences
    def create_central_widget(self) -> None:
        central = QWidget()

        # Main layout
        layout = QHBoxLayout()

        # Tags
        v_box = QVBoxLayout()

        # Buttons of tags
        buttons = QHBoxLayout()
        reload_button = QPushButton('Reload')
        reload_button.clicked.connect(self.reload_tags)
        buttons.addWidget(reload_button)
        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(self.delete_tags)
        buttons.addWidget(delete_button)
        add_button = QPushButton('Add')
        add_button.clicked.connect(self.add_tag)
        buttons.addWidget(add_button)
        v_box.addLayout(buttons)

        # Sorting of tags
        combo = QComboBox()
        combo.addItems(['sort by count',
                        'sort by used time',
                        'sort by alphabet'])
        combo.currentIndexChanged[str].connect(self.select_tag_list)
        v_box.addWidget(combo)

        # Lists of tags
        h_box = QHBoxLayout()
        h_box.addWidget(self.tag_list_by_alphabet)
        h_box.addWidget(self.tag_list_by_time)
        h_box.addWidget(self.tag_list_by_count)
        v_box.addLayout(h_box)

        # Lists of files
        files_box_layout = QVBoxLayout()
        files_box_layout.addWidget(self.file_list)
        self.files_box.setLayout(files_box_layout)

        layout.addLayout(v_box)
        layout.addWidget(self.files_box)
        layout.addWidget(self.file_info_box)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def select_tag_list(self, name) -> None:
        if name == 'sort by count':
            self.current_tag_list = self.tag_list_by_count
            self.tag_list_by_count.setVisible(True)
            self.tag_list_by_time.setVisible(False)
            self.tag_list_by_alphabet.setVisible(False)
        elif name == 'sort by used time':
            self.current_tag_list = self.tag_list_by_time
            self.tag_list_by_count.setVisible(False)
            self.tag_list_by_time.setVisible(True)
            self.tag_list_by_alphabet.setVisible(False)
        elif name == 'sort by alphabet':
            self.current_tag_list = self.tag_list_by_alphabet
            self.tag_list_by_count.setVisible(False)
            self.tag_list_by_time.setVisible(False)
            self.tag_list_by_alphabet.setVisible(True)
        self.update_file_list(self.current_tag_list.currentItem())

    def reload_tags(self) -> None:
        self.update_all_tag_lists()

    def delete_tags(self) -> None:
        deleted_items = get_checked_items(self.current_tag_list)
        if not deleted_items:
            return

        answer = QMessageBox.question(
            self,
            "Delete permanently",
            "Can not recover, really want to delete?",
            defaultButton=QMessageBox.No)

        if answer == QMessageBox.No:
            return

        for item in deleted_items:
            tag = item.data(Qt.UserRole)
            self.delete_or_edit_tag(tag, '')
            self.db.delete_tag(tag)

        self.db.commit()
        self.update_all_tag_lists()

    def delete_or_edit_tag(self, deleted: str, added: str) -> None:

        if not deleted:
            raise ValueError("'deleted' should be a non-empty string")

        if added:
            """ The situation of edit """
            added = {added}
        else:
            """ The situation of delete """
            added = set()

        for file in self.db.get_bijis(deleted):
            biji = Biji.from_file(file)
            biji.tags = self.generate_new_tags(set(biji.tags),
                                               {deleted},
                                               added)
            biji.write_file()
            self.db.update_biji_mtime(file, biji.bijiMTime)

    def add_tag(self) -> None:
        pass

    def edit_tag(self, index: QModelIndex) -> None:
        old_tag = index.data(Qt.UserRole)

        tag, ok = QInputDialog.getText(
            self,
            "Edit",
            f"(all relative files will be affected.)\n"
            f"Change '{old_tag}' to:")

        tag = tag.strip()
        if not ok or len(tag) == 0:
            return

        if self.db.get_tag_atime(tag):
            QMessageBox.information(
                self, "Duplicated.", "The tag is already in the list.\n",
                QMessageBox.Close)
            return

        self.delete_or_edit_tag(old_tag, tag)
        self.db.update_tag(old_tag, tag)
        self.update_all_tag_lists()

    def update_file_list(self, current: QListWidgetItem) -> None:
        self.file_list.clear()

        if current is None:
            self.files_box.setTitle(f'Files')
            return

        tag = current.data(Qt.UserRole)
        for file in self.db.get_bijis(tag):
            item = QListWidgetItem(self.file_list)
            item.setText(file)
        self.files_box.setTitle(f'Files - [{self.file_list.count()}]')
        self.file_list.setCurrentRow(0)

    def update_file_info(self, current: QListWidgetItem) -> None:
        self.file_info_box.update_file_info(current)


if __name__ == '__main__':

    import sys

    from .. import change_cwd
    change_cwd()

    app = QApplication(sys.argv)
    window = BijitagsManager()
    window.show()
    sys.exit(app.exec_())
