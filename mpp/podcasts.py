from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    QCoreApplication,
    pyqtSignal,
    QThread,
    QVariant
)
from PyQt5.QtGui import QFont
from urllib.request import urlopen
from .ui import Ui_add_dialog
from .utils import getAppDataDir, isLinux
from . import db
import re
import urllib.parse
import json
_translate = QCoreApplication.translate


class addDialog(QtWidgets.QDialog):
    """Employee dialog."""
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_add_dialog.Ui_addDialog()
        self.ui.setupUi(self)
        self.callback = callback

        self.ui.addUrlBtn.clicked.connect(self.fromUrl)
        self.ui.searchBtn.clicked.connect(self.search)
        self.ui.searchResult.clicked.connect(self.resultSelected)
        self.ui.addSearchBtn.clicked.connect(self.addFromSearch)

    def fromUrl(self, url=None):
        if not url:
            url = self.ui.addUrlInput.text()

        ivoox = re.findall('(https?:\/\/www\.ivoox\.com\/)([a-z0-9\-]+)_sq_([a-z0-9\-]+)_1\.html', url)
        if ivoox:
            ivoox = ivoox[0]
            url = 'https://www.ivoox.com/{0}_fg_{1}_filtro_1.xml'.format(ivoox[1], ivoox[2])
        self.addPCThread = db.addPodcast(self, url)
        self.addPCThread.podcast.connect(self.callback)
        self.addPCThread.start()

    def search(self):
        terms = self.ui.searchInput.text()
        if terms != '':
            self.ui.searchResult.clear()
            thread = itunes(self, terms)
            thread.itune.connect(self.addResult)
            thread.start()

    def addResult(self, data):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(1)
        widget.setLayout(layout)

        font = QFont()

        label1 = QtWidgets.QLabel(data['collectionName'])
        layout.addWidget(label1)

        font.setPointSize(8)

        label2 = QtWidgets.QLabel(data['artistName'])
        label2.setFont(font)
        layout.addWidget(label2)

        item = QtWidgets.QListWidgetItem()

        minimumSizeHint = self.ui.searchResult.minimumSizeHint()
        minimumSizeHint.setHeight(48)
        item.setSizeHint(minimumSizeHint)

        self.ui.searchResult.addItem(item)
        self.ui.searchResult.setItemWidget(item, widget)

        item.value = data['feedUrl']
        self.ui.searchResult.addItem(item)

    def resultSelected(self, w):
        if not self.ui.addSearchBtn.isEnabled():
            self.ui.addSearchBtn.setEnabled(True)

    def addFromSearch(self):
        url = self.ui.searchResult.currentItem().value
        self.fromUrl(url)


class itunes(QThread):
    itune = pyqtSignal(QVariant)
    baseUrl = 'https://itunes.apple.com/search'

    def __init__(self, parent, terms):
        super(itunes, self).__init__(parent)
        self.terms = terms

    def run(self):
        data = {}
        data['term'] = self.terms
        data['media'] = 'podcast'
        url_values = urllib.parse.urlencode(data)
        full_url = self.baseUrl + '?' + url_values
        with urlopen(full_url) as response:
            rawData = response.read().decode('utf-8')
            data = json.loads(rawData)
            for result in data['results']:
                if 'feedUrl' in result:
                    self.itune.emit(result)
