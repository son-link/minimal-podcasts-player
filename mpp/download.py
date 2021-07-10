from urllib import request
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSignal, QThread

from .conf import getConf
from .utils import getAppCacheDir
from .db import addDownLocalfile
from os import path
import pathlib

cache_dir = getAppCacheDir()

downList = []
currentPos = -1
is_dw = False


class Downloads():
    def __init__(self):
        super().__init__()

    def add(self, parent, data, player):
        global currentPos, downList, is_dw
        if data:
            widget = Widget(parent, data, player)
            downList.append(widget)
            if not is_dw:
                currentPos += 1
                is_dw = True
                self.nextDown()
            return widget

    @staticmethod
    def nextDown():
        w = downList[currentPos]
        thread = downloadAudio(w.parent, w.url, w.filename)
        thread.percent.connect(w.updatePB)
        thread.start()


class Widget(QtWidgets.QWidget):
    """
        The widget use in the downloads width
    """
    def __init__(self, parent=None, data=None, player=None):
        super(Widget, self).__init__(parent)
        self.parent = parent
        self.player = player

        self.setStyleSheet('background-color: transparent')
        self.setFixedHeight(48)
        self.conf = getConf()

        font = QFont()
        font.setPointSize(10)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(1)

        coverLabel = QtWidgets.QLabel()
        layout.addWidget(coverLabel)
        coverImage = QPixmap(cache_dir+'/'+data['cover'])
        coverLabel.setPixmap(coverImage.scaled(
            40,
            40,
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        self.infoWidget = QtWidgets.QWidget()
        layout2 = QtWidgets.QVBoxLayout()
        self.infoWidget.setLayout(layout2)

        self.title = QtWidgets.QLabel(data['title'])
        self.title.setFont(font)
        layout2.addWidget(self.title)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setFixedHeight(10)
        layout2.addWidget(self.progressBar)

        layout.addWidget(self.infoWidget)
        layout.addStretch(1)

        layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(layout)

        self.idEpisode = data['idEpisode']

        name = ''
        if 'rename_download' in self.conf and self.conf['rename_download']:
            name = data['title'] + '.mp3'
        else:
            name = data['url'].split('/')[-1]
        directory = path.join(self.conf['download_folder'], data['pc_title'])
        pathlib.Path(directory).mkdir(parents=True, exist_ok=True)

        self.filename = path.join(directory, name)
        self.url = data['url']

    def updatePB(self, percent):
        global currentPos, downList, is_dw
        self.progressBar.setValue(percent)
        if percent == 100:
            addDownLocalfile(self.idEpisode, self.filename)
            self.player.changeUrl(self.idEpisode, 'file://' + self.filename)
            if currentPos < len(downList) - 1:
                currentPos += 1
                Downloads.nextDown()
            else:
                is_dw = False


class downloadAudio(QThread):
    percent = pyqtSignal(int)

    def __init__(self, parent, url, filename):
        super(downloadAudio, self).__init__(parent)
        self.url = url
        self.filename = filename

    def run(self):
        request.urlretrieve(self.url, self.filename, self.show_progress)

    def show_progress(self, block_num, block_size, total_size):
        global downList, currentPos
        downloaded = (block_num * block_size / total_size)*100
        if downloaded < total_size:
            self.percent.emit(downloaded)
        else:
            self.percent.emit(100)
