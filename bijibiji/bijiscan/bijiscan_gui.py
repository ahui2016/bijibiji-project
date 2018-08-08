from pathlib import Path
from typing import List

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QListWidget, \
    QVBoxLayout, QPushButton, QApplication, QListWidgetItem, QMessageBox

from ..bijidb.bijidatabase import BijiDatabase
from ..bijitags.biji import Biji


# noinspection PyArgumentList,PyCallByClass
class BijiScanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.db = BijiDatabase
        try:
            self.db.connect_db()
        except FileNotFoundError:
            BijiDatabase.create_db()
            self.db.connect_db()

        self.no_file_box = QGroupBox()
        self.new_file_box = QGroupBox()
        self.outdated_box = QGroupBox()
        self.no_json_box = QGroupBox()

        self.no_file_list = QListWidget(self.no_file_box)
        self.new_file_list = QListWidget(self.new_file_box)
        self.outdated_list = QListWidget(self.outdated_box)
        self.no_json_list = QListWidget(self.no_json_box)

        self.files_not_exists = []
        self.not_in_database = []
        self.need_to_update = []
        self.biji_json_not_exists = []

        self.scan_all()
        self.get_biji_json_not_exists()

        self.update_list(self.no_file_list, self.files_not_exists)
        self.update_list(self.new_file_list, self.not_in_database)
        self.update_list(self.outdated_list, self.need_to_update)
        self.update_list(self.no_json_list, self.biji_json_not_exists)

        self._init_ui_()

    def _init_ui_(self) -> None:
        self.setWindowTitle('BijiScanner - bijibiji')

        layout = QHBoxLayout()

        self.no_file_box.setTitle('Files not exist')
        self.no_file_box.setToolTip(
            "'.biji.json' file exists, but the corresponding \n"
            "original file is not found.")
        no_file_box_layout = QVBoxLayout()
        no_file_box_layout.addWidget(self.no_file_list)
        no_file_box_buttons = QHBoxLayout()
        self.delete_biji_json_file_btn = QPushButton('Delete all')
        self.delete_biji_json_file_btn.clicked.connect(
            self.delete_biji_json_files)
        no_file_box_buttons.addStretch(1)
        no_file_box_buttons.addWidget(self.delete_biji_json_file_btn)
        no_file_box_layout.addLayout(no_file_box_buttons)
        self.no_file_box.setLayout(no_file_box_layout)

        self.new_file_box.setTitle('New files found')
        self.new_file_box.setToolTip(
            'New files that can be added to the database.')
        new_file_box_layout = QVBoxLayout()
        new_file_box_layout.addWidget(self.new_file_list)
        new_file_box_buttons = QHBoxLayout()
        self.add_to_database_btn = QPushButton('Add all')
        self.add_to_database_btn.clicked.connect(self.add_to_database)
        new_file_box_buttons.addStretch(1)
        new_file_box_buttons.addWidget(self.add_to_database_btn)
        new_file_box_layout.addLayout(new_file_box_buttons)
        self.new_file_box.setLayout(new_file_box_layout)

        self.outdated_box.setTitle('Outdated files')
        self.outdated_box.setToolTip('Files that need to be updated.')
        outdated_box_layout = QVBoxLayout()
        outdated_box_layout.addWidget(self.outdated_list)
        outdated_box_buttons = QHBoxLayout()
        self.update_btn = QPushButton('Update all')
        self.update_btn.clicked.connect(self.update_database)
        outdated_box_buttons.addStretch(1)
        outdated_box_buttons.addWidget(self.update_btn)
        outdated_box_layout.addLayout(outdated_box_buttons)
        self.outdated_box.setLayout(outdated_box_layout)

        self.no_json_box.setTitle("'.biji.json' not exist")
        self.no_json_box.setToolTip(
            'Records in the database, but the corresponding \n'
            '.biji.json file is not found.')
        no_json_box_layout = QVBoxLayout()
        no_json_box_layout.addWidget(self.no_json_list)
        no_json_box_buttons = QHBoxLayout()
        self.delete_records_btn = QPushButton('Delete all')
        self.delete_records_btn.clicked.connect(self.delete_records)
        no_json_box_buttons.addStretch(1)
        no_json_box_buttons.addWidget(self.delete_records_btn)
        no_json_box_layout.addLayout(no_json_box_buttons)
        self.no_json_box.setLayout(no_json_box_layout)

        layout.addWidget(self.no_file_box)
        layout.addWidget(self.new_file_box)
        layout.addWidget(self.outdated_box)
        layout.addWidget(self.no_json_box)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.db.close_db()
        event.accept()

    @staticmethod
    def update_list(list_widget: QListWidget, items: List[str]) -> None:
        if not items:
            list_widget.parent().setVisible(False)
            return
        for item in items:
            list_item = QListWidgetItem(list_widget)
            list_item.setText(item)

    def scan_all(self) -> None:
        end = -len('.biji.json')

        biji_paths = Path('.').glob('**/*.biji.json')
        for biji_path in biji_paths:
            file = str(biji_path)[:end]
            if Path(file).exists():
                biji = Biji.from_file(file)
            else:
                self.files_not_exists.append(file)
                continue

            mtime = self.db.get_mtime(file)
            if not mtime:
                self.not_in_database.append(file)
                continue

            if biji.bijiMTime > mtime:
                self.need_to_update.append(file)

    def get_biji_json_not_exists(self) -> None:
        for row in self.db.get_all_filepaths():
            filepath = row['filepath']
            if not Biji.get_biji_json_path(filepath).exists():
                self.biji_json_not_exists.append(filepath)

    def show_done_message(self) -> None:
        QMessageBox.information(self, "Result.", "Done.\n", QMessageBox.Close)

    def delete_biji_json_files(self) -> None:
        if not self.files_not_exists:
            return
        answer = QMessageBox.question(
            self,
            "Delete permanently",
            "Really delete all .biji.json files?",
            defaultButton=QMessageBox.No)
        if answer == QMessageBox.No:
            return
        for file in self.files_not_exists:
            biji_json_file = Biji.get_biji_json_path(file)
            Path(biji_json_file).unlink()
        self.show_done_message()
        self.no_file_box.setEnabled(False)

    def add_to_database(self) -> None:
        if not self.not_in_database:
            return
        for file in self.not_in_database:
            biji = Biji.from_file(file)
            biji.insert_biji_and_tags_to_db()
        self.show_done_message()
        self.new_file_box.setEnabled(False)

    def update_database(self) -> None:
        if not self.need_to_update:
            return
        for file in self.need_to_update:
            biji = Biji.from_file(file)
            biji.update_biji_and_tags_to_db()
        self.show_done_message()
        self.outdated_box.setEnabled(False)

    def delete_records(self) -> None:
        if not self.biji_json_not_exists:
            return
        for file in self.biji_json_not_exists:
            self.db.delete_biji(file)
        self.show_done_message()
        self.no_json_box.setEnabled(False)


if __name__ == '__main__':

    import sys

    from .. import change_cwd
    change_cwd()

    app = QApplication(sys.argv)
    window = BijiScanner()
    window.show()
    sys.exit(app.exec_())
