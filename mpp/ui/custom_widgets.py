# -*- coding: utf-8 -*-
"""
This file include all custom widgets use in the program
"""

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QFont
from ..utils import getAppCacheDir, coverExist, downloadCover

cache_dir = getAppCacheDir()


class podcastWidget(QtWidgets.QWidget):

    """
        The widget use in the podcasts list
    """
    def __init__(self, parent=None, data=None):
        super(podcastWidget, self).__init__(parent)
        self.setStyleSheet('background-color: transparent')
        self.setFixedHeight(48)
        font = QFont()
        font.setPointSize(10)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(1)

        coverLabel = QtWidgets.QLabel()
        layout.addWidget(coverLabel)

        if coverExist(data['cover']):
            coverImage = QPixmap(cache_dir+'/'+data['cover'])
            coverLabel.setPixmap(
                coverImage.scaled(
                    40,
                    40,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        else:
            downloadCover(data['coverUrl'], data['cover'])
            coverImage = QPixmap(cache_dir+'/'+data['cover'])
            coverLabel.setPixmap(
                coverImage.scaled(
                    40,
                    40,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        self.infoWidget = QtWidgets.QWidget()

        layout2 = QtWidgets.QVBoxLayout()
        # layout2.setSpacing(0)
        self.infoWidget.setLayout(layout2)

        title = QtWidgets.QLabel(data['title'])
        title.setFont(font)
        layout2.addWidget(title)

        font.setPointSize(8)
        label = QtWidgets.QLabel(
            '{} episodio(s)'.format(data['total_episodes'])
        )
        label.setFont(font)
        layout2.addWidget(label)

        layout.addWidget(self.infoWidget)
        layout.addStretch(1)

        layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(layout)


class queueWidget(QtWidgets.QWidget):
    def __init__(self, data=None):
        super(queueWidget, self).__init__()
        self.setFixedHeight(64)
        font = QFont()
        font.setPointSize(9)

        layout = QtWidgets.QHBoxLayout()

        self.statusIcon = QtWidgets.QLabel()
        self.statusIcon.setFixedSize(24, 24)
        layout.addWidget(self.statusIcon)

        coverLabel = QtWidgets.QLabel()
        layout.addWidget(coverLabel)
        coverImage = QPixmap(cache_dir+'/'+data['cover'])
        coverLabel.setPixmap(coverImage.scaled(48, 32, Qt.KeepAspectRatio))

        self.infoWidget = QtWidgets.QWidget()

        layout2 = QtWidgets.QVBoxLayout()
        self.infoWidget.setLayout(layout2)

        title = QtWidgets.QLabel(data['pc_title'])
        layout2.addWidget(title)

        label = QtWidgets.QLabel(data['title'])
        label.setFont(font)
        layout2.addWidget(label)

        layout.addWidget(self.infoWidget)
        layout.addStretch(1)

        layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(layout)
