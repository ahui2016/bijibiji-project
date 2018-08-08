import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWizard, QApplication

from ..bijidb.bijidatabase import BijiDatabase
from .add_file_page import AddFilePage
from .preview_page import PreviewPage
from .result_page import ResultPage
from .tags_page import TagsPage


# noinspection PyArgumentList
class BijitagsWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = BijiDatabase
        try:
            self.db.connect_db()
        except FileNotFoundError:
            self.db.create_db()
            self.db.connect_db()

        print(os.getcwd())

        self.setWindowTitle('bijitags - bijibiji')
        self.setWindowFlags(
            Qt.CustomizeWindowHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.setWizardStyle(QWizard.ModernStyle)
        self.setButtonLayout([QWizard.BackButton,
                              QWizard.Stretch,
                              QWizard.NextButton,
                              QWizard.FinishButton])
        self.add_file_page = AddFilePage()
        self.tags_page = TagsPage()
        self.preview_page = PreviewPage()
        self.result_page = ResultPage(self)
        self.setPage(1, self.add_file_page)
        self.setPage(2, self.tags_page)
        self.setPage(3, self.preview_page)
        self.setPage(4, self.result_page)

        self.setOptions(QWizard.NoBackButtonOnStartPage
                        | QWizard.NoBackButtonOnLastPage)

    def initializePage(self, p_int):
        if p_int == 2:
            self.tags_page.files = self.add_file_page.files
            # self.tags_page.initializePage()

        if p_int == 3:
            self.preview_page.files = self.add_file_page.files
            self.preview_page.new_common_tags = self.tags_page.new_common_tags
            self.preview_page.old_common_tags = self.tags_page.common_tags
            # self.preview_page.initializePage()

        super().initializePage(p_int)

    def done(self, p_int):
        current_page = self.currentPage()
        if self.currentId() == 4 \
                and hasattr(current_page, 'to_be_restart') \
                and current_page.to_be_restart:
            self.add_file_page.files.clear()
            self.add_file_page.fileList.clear()
            self.add_file_page.filesBox.setTitle('Files')
            self.restart()
        else:
            super().done(p_int)

    def closeEvent(self, event):
        self.db.close_db()
        event.accept()


if __name__ == '__main__':

    import sys

    from .. import change_cwd
    change_cwd()

    app = QApplication(sys.argv)
    wizard = BijitagsWizard()
    wizard.show()
    sys.exit(app.exec_())
