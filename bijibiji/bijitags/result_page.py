from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWizardPage, QWizard, QLabel, QVBoxLayout, \
    QHBoxLayout, QPushButton


# noinspection PyAttributeOutsideInit,PyArgumentList
class ResultPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent: QWizard = parent
        self.setTitle("Result")
        self.setButtonText(QWizard.FinishButton, "Close")
        self._init_ui_()

    def _init_ui_(self):
        result = QLabel("All changes have been saved.\n")
        result.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(result)

        button_layout = QHBoxLayout()
        restart_button = QPushButton('Go Back')
        restart_button.clicked.connect(self.go_back)
        button_layout.addStretch(1)
        button_layout.addWidget(restart_button)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def initializePage(self):
        self.to_be_restart = False

    def go_back(self):
        self.to_be_restart = True
        self.parent.done(0)
