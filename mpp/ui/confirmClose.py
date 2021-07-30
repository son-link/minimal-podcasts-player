from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QPushButton
)
from PyQt5.QtCore import QCoreApplication, Qt
from sys import exit as sysExit

_translate = QCoreApplication.translate


class confirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint)
        self.setWindowTitle(_translate('confirmClose', 'Close'))

        self.layout = QVBoxLayout()
        message = QLabel(
            _translate(
                'confirmClose',
                'Are you sure you want to close the application?'
            )
        )

        self.buttonBox = QDialogButtonBox()
        closeBtn = QPushButton(_translate('confirmClose', 'Close'))
        closeBtn.clicked.connect(self.close)
        self.buttonBox.addButton(closeBtn, QDialogButtonBox.ActionRole)

        miniBtn = QPushButton(_translate('confirmClose', 'Minimize to tray'))
        miniBtn.clicked.connect(self.hideMW)
        self.buttonBox.addButton(miniBtn, QDialogButtonBox.ActionRole)

        closeBtn = QPushButton(_translate('confirmClose', 'Cancel'))
        closeBtn.clicked.connect(self.hide)
        self.buttonBox.addButton(closeBtn, QDialogButtonBox.ActionRole)

        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        self.show()

    def close(self):
        sysExit()

    def hideMW(self):
        self.hide()
        self.parent.hide()
        self.parent.isMWShow = False
