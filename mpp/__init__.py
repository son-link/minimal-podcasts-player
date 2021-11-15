from os import path
from .ui import Ui_gui
from PyQt5.QtCore import (
    Qt,
    QCoreApplication,
    QLocale,
    QTranslator
)
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QCursor, QPixmap
from math import ceil
from .player import Player
from .utils import (
    addNewEpidodes,
    getAppDataDir,
    getAppCacheDir,
    isLinux,
    isBSD
)
from .ui import custom_widgets as cw
from .ui import confirmClose
from .ui import Ui_about
from . import db
from . import conf
from . import podcasts
from . import download
from . import opml
from time import sleep
from sys import exit as sysExit

import re
import os

_translate = QCoreApplication.translate

db_dir = getAppDataDir()
cache_dir = getAppCacheDir()

# Check if the database file exists, and if so, create it.
db_file = path.join(db_dir, 'mpp.db')
if not path.exists(db_file):
    db.createDB()
    sleep(2)
else:
    # If exists check if necessary update the database
    db.updateDB()


class MainWindow(QtWidgets.QMainWindow, Ui_gui.Ui_MainWindow):
    """
    The main window
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.config = conf.getConf()  # Get the config
        self.currentPage = 0
        self.totalPages = 1
        self.isMWShow = True

        self.player = Player(self)

        self.menu = QtWidgets.QMenu()

        self.actionAdd = QtWidgets.QAction(
            _translate('MainWindow', 'Add podcast'),
            self
        )
        self.actionAdd.triggered.connect(self.addPodcast)
        self.menu.addAction(self.actionAdd)

        self.actionUpdate = QtWidgets.QAction(
            _translate('MainWindow', 'Update'),
            self
        )
        self.actionUpdate.triggered.connect(self.getNewEpisodes)
        self.menu.addAction(self.actionUpdate)

        self.actionConfig = QtWidgets.QAction(
            _translate('MainWindow', 'Configure'),
            self
        )
        self.actionConfig.triggered.connect(self.showConfDialog)
        self.menu.addAction(self.actionConfig)
        
        self.actionImport = QtWidgets.QAction(
            _translate('MainWindow', 'Import suscriptions'),
            self
        )
        self.actionImport.triggered.connect(self.import_opml)
        self.menu.addAction(self.actionImport)

        self.actionAbout = QtWidgets.QAction(
            _translate('MainWindow', 'About'),
            self
        )
        self.actionAbout.triggered.connect(self.showAboutDialog)
        self.menu.addAction(self.actionAbout)

        self.optionsBtn.setMenu(self.menu)

        self.splitter.setStretchFactor(1, 2)

        self.podcastsList.customContextMenuRequested.connect(self.podcastsMenu)

        self.episodesTable.setColumnCount(4)
        self.episodesTable.setHorizontalHeaderLabels(
            [
                _translate('MainWindow', 'Episode'),
                _translate('MainWindow', 'Published'),
                _translate('MainWindow', 'Duration'),
                ''
            ]
        )
        self.episodesTable.customContextMenuRequested.connect(
            self.episodesMenu
        )
        self.episodesTable.doubleClicked.connect(self.dcPlayEpisode)
        self.episodesTable.setWordWrap(True)

        self.queueList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.queueList.customContextMenuRequested.connect(self.queueMenu)

        icon = QIcon.fromTheme("audio-volume-high")
        self.iconVol.setPixmap(icon.pixmap(16, 16))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setValue(self.player.volume)

        self.episodesCount = 0
        self.episodesData = []
        self.podcastSelected = 0
        self.prependEpisodes = False

        # Connect events
        self.timeSlider.valueChanged.connect(self.player.setPosition)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)
        self.podcastsList.clicked.connect(self.getEpisodes)
        self.playBtn.clicked.connect(self.player.playPause)
        self.stopBtn.clicked.connect(self.player.stop)
        self.back10Btn.clicked.connect(self.player.rev10Secs)
        self.for10Btn.clicked.connect(self.player.for10Secs)
        self.queueList.clicked.connect(self.getEpisodeData)
        self.queueList.doubleClicked.connect(self.changeEpisode)
        self.queuePrevBtn.clicked.connect(self.player.queueList.previous)
        self.queueNextBtn.clicked.connect(self.player.queueList.next)

        # Multimedia keys
        self.playBtn.setShortcut(Qt.Key_MediaPlay)
        self.stopBtn.setShortcut(Qt.Key_MediaStop)
        self.queuePrevBtn.setShortcut(Qt.Key_MediaPrevious)
        self.queueNextBtn.setShortcut(Qt.Key_MediaNext)

        self.prevDataBtn.clicked.connect(self.paginationPrev)
        self.nextDataBtn.clicked.connect(self.paginationNext)

        # Tray icon
        self.tray = QtWidgets.QSystemTrayIcon(
            QIcon(QPixmap(':/img/icon.svg')),
            self
        )

        # Tray menu
        trayMenu = QtWidgets.QMenu()
        self.trayPlay = QtWidgets.QAction(
            QIcon.fromTheme('media-playback-start'),
            _translate('MainWindow', 'Play/Pause'),
            trayMenu
        )
        self.trayPlay.triggered.connect(self.player.playPause)
        trayMenu.addAction(self.trayPlay)

        prevAction = QtWidgets.QAction(
            QIcon.fromTheme('media-skip-backward'),
            _translate('MainWindow', 'Previous track'),
            trayMenu
        )
        prevAction.triggered.connect(self.player.queueList.previous)
        trayMenu.addAction(prevAction)

        nextAction = QtWidgets.QAction(
            QIcon.fromTheme('media-skip-forward'),
            _translate('MainWindow', 'Next track'),
            trayMenu
        )
        nextAction.triggered.connect(self.player.queueList.next)
        trayMenu.addAction(nextAction)

        stopAction = QtWidgets.QAction(
            QIcon.fromTheme('media-playback-stop'),
            _translate('MainWindow', 'Stop'),
            trayMenu
        )
        stopAction.triggered.connect(self.player.stop)
        trayMenu.addAction(stopAction)

        showHideAction = QtWidgets.QAction(
            QIcon.fromTheme('dashboard-show'),
            _translate('MainWindow', 'Hide/Show'),
            trayMenu
        )
        showHideAction.triggered.connect(self.hideShowMW)
        trayMenu.addAction(showHideAction)

        closeAction = QtWidgets.QAction(
            QIcon.fromTheme('application-exit'),
            _translate('MainWindow', 'Quit'),
            trayMenu
        )
        closeAction.triggered.connect(sysExit)
        trayMenu.addAction(closeAction)

        self.tray.setContextMenu(trayMenu)
        self.tray.setToolTip('Minimal Podcasts Player')

        self.tray.setVisible(True)
        self.tray.activated.connect(self.hideShowMW)

        thread = db.getPodcasts(self)
        thread.podcast.connect(self.addPCList)
        thread.start()
        if self.config['update_on_init']:
            self.getNewEpisodes()

        self.dw = download.Downloads()

    def playPodcast(self, pressed):
        """ Starts playing a episode when the play button
            in the episode list is clicked.
            Args:
                pressed : object
                    The button pressed
            Returns:
                True if he podcasts is remove correctly
                or False in case of error
        """

        source = self.sender()
        pos = source.value

        self.player.queueData = []
        self.queueList.clear()
        self.player.queueList.clear()
        self.add2queue(pos)
        self.player.startPlay()

    def addPCList(self, data):
        """ This is a callback function called when
            add a podcast to the list
            Args:
                data : dict
                    The podcast's data
            Returns:
                True if he podcasts is remove correctly
                or False in case of error
        """

        item = cw.podcastWidget(self, data)
        myItem = QtWidgets.QListWidgetItem()
        myItem.value = data['idPodcast']
        item.setProperty('class', 'podcast')
        self.podcastsList.addItem(myItem)
        self.podcastsList.setItemWidget(myItem, item)
        minimumSizeHint = self.podcastsList.minimumSizeHint()
        minimumSizeHint.setHeight(48)
        myItem.setSizeHint(minimumSizeHint)

    def addPodcast(self):
        """Show the Add podcast dialog"""
        self.addDialog = podcasts.addDialog(self, self.addNewToList)
        self.addDialog.exec_()

    def addNewToList(self, idPodcast, length):
        """ This is a callback function called when
            add a new episodes to the list
            and one is selected
            Args:
                idPodcast : int
                    The podcast's identifier
                length:
                    How many of episodes are in the database
        """
        if (idPodcast and idPodcast != 0):
            self.addDialog.close()
            data = db.getPodcast(idPodcast)
            data['total_episodes'] = length
            item = cw.podcastWidget(self, data)
            myItem = QtWidgets.QListWidgetItem()
            myItem.value = data['idPodcast']
            self.podcastsList.addItem(myItem)
            self.podcastsList.setItemWidget(myItem, item)
            minimumSizeHint = self.podcastsList.minimumSizeHint()
            minimumSizeHint.setHeight(48)
            myItem.setSizeHint(minimumSizeHint)
            self.statusBar().showMessage('')

    def reloadPCList(self, reload):
        """ Reload the podcasts list
            Args:
                reload : bool
                    True for reload
        """
        if reload:
            self.podcastsList.clear()
            thread = db.getPodcasts(self)
            thread.podcast.connect(self.addPCList)
            thread.start()

    def add2queue(self, pressed, pos=None):
        """ Add episode to the playlist queue
            Args:
                pressed : object
                    The button pressed
                pos : int, optional
                    The episode position on the list. This parameter is passed
                    when using the submenu of the list.
            Returns:
                True if he podcasts is remove correctly
                or False in case of error
        """
        if not pos and pos != 0:
            source = self.sender()
            pos = source.value

        data = self.episodesData[pos]
        self.player.add(data)

        item = cw.queueWidget(data)

        myItem = QtWidgets.QListWidgetItem()

        self.queueList.addItem(myItem)
        self.queueList.setItemWidget(myItem, item)
        minimumSizeHint = self.queueList.minimumSizeHint()
        minimumSizeHint.setHeight(64)
        myItem.setSizeHint(minimumSizeHint)

        if self.player.queueList.mediaCount() > 1:
            self.queueNextBtn.setEnabled(True)

    def getEpisodes(self, item=None):
        """ Get and show the selected podcast's episodes
            Args:
                item : object, optional
                    The podcast selected
        """
        self.episodesCount = 0
        self.lastEpisodePos = 0
        self.episodesData = []
        idPodcast = self.podcastsList.currentItem().value
        info = db.getPodcast(idPodcast)
        self.podcastTitle.setText(info['title'])
        self.podcastWeb.setText(
            '<a href="{0}">{0}</a>'.format(info['pageUrl'])
        )
        description = re.sub(
            r'(https?:\/\/[^\s]+)', r'<a href="\g<0>">\g<0></a>',
            info['description']
        )

        coverImage = QPixmap(cache_dir+'/'+info['cover'])
        self.podcastCover.setPixmap(
            coverImage.scaled(128, 128, Qt.KeepAspectRatio)
        )

        if item:
            totalEpisodes = db.getTotalEpisodes(idPodcast)
            self.currentPage = 0
            self.totalPages = ceil(
                totalEpisodes / self.config['episodes_per_page']
            )

        offset = (self.currentPage * self.config['episodes_per_page']) + 1
        self.podcastDesc.setText(description)
        thread = db.getEpisodes(
            self,
            idPodcast,
            offset,
            self.config['episodes_per_page']
        )
        thread.episodes.connect(self.insertEpisode)
        thread.start()
        self.podcastSelected = idPodcast
        self.paginationLabel.setText(
                _translate(
                    'MainWindow',
                    'Page {0} of {1}'
                ).format(self.currentPage+1, self.totalPages)
            )

    def insertEpisode(self, data, preppend=False):
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout()

        btnWidget.setProperty('class', 'episode')
        btnLayout.setContentsMargins(1, 1, 1, 1)
        btnWidget.setLayout(btnLayout)

        playIcon = QIcon.fromTheme('media-playback-start')
        btnPlayEpisode = QtWidgets.QPushButton(playIcon, '')
        btnPlayEpisode.value = self.lastEpisodePos
        btnPlayEpisode.setFlat(True)
        btnPlayEpisode.setProperty('class', 'episode_btn')
        btnPlayEpisode.clicked.connect(self.playPodcast)
        btnLayout.addWidget(btnPlayEpisode)

        addIcon = QIcon.fromTheme('list-add')
        btnAdd = QtWidgets.QPushButton(addIcon, '')
        btnAdd.value = self.lastEpisodePos
        btnAdd.setFlat(True)
        btnPlayEpisode.setProperty('class', 'episode_btn')
        btnAdd.clicked.connect(self.add2queue)
        btnLayout.addWidget(btnAdd)

        downIcon = QIcon.fromTheme('go-down')
        btnDown = QtWidgets.QPushButton(downIcon, '')
        btnDown.value = self.lastEpisodePos
        btnDown.setFlat(True)
        btnDown.clicked.connect(self.addDownload)
        btnLayout.addWidget(btnDown)

        btnLayout.addStretch(1)

        self.episodesData.append(data)
        self.episodesCount += 1
        pos = self.episodesCount - 1

        if preppend:
            pos = 0

        self.episodesTable.insertRow(pos)
        self.episodesTable.setRowCount(self.episodesCount)
        self.episodesTable.setItem(pos, 0, QtWidgets.QTableWidgetItem(''))
        title = '{0}'.format(data['title'])
        self.episodesTable.setItem(
            pos,
            0,
            QtWidgets.QTableWidgetItem(title)
        )
        self.episodesTable.setItem(
            pos,
            1,
            QtWidgets.QTableWidgetItem(data['date_format'])
        )
        self.episodesTable.setItem(
            pos,
            2,
            QtWidgets.QTableWidgetItem(str(data['totalTime']))
        )
        self.episodesTable.setCellWidget(pos, 3, btnWidget)

        header = self.episodesTable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self.lastEpisodePos += 1
        # self.episodesTable.resizeRowsToContents()

    def getEpisodeData(self, item):
        row = item.row()
        data = self.player.queueData[row]
        description = '<h3>%s</h3>' % data['title']
        description += _translate(
            'MainWindow',
            '<p>Subido el {}</p>'.format(data['date'])
        )
        description += data['description']
        self.infoEpisodeLabel.setText(description)

    def episodesMenu(self, event):
        menu = QtWidgets.QMenu(self.episodesTable)
        addIcon = QIcon.fromTheme('list-add')
        addAction = QtWidgets.QAction(
            addIcon,
            _translate('MainWindow', 'Add to queue'),
            self
        )
        addAction.triggered.connect(self.getEpisodesSelecteds)
        menu.addAction(addAction)

        downIcon = QIcon.fromTheme('go-down')
        downAction = QtWidgets.QAction(
            downIcon,
            _translate('MainWindow', 'Add to download queue'),
            self
        )
        downAction.triggered.connect(self.addDownloads)
        menu.addAction(downAction)
        # add other required actions
        menu.popup(QCursor.pos())

    def getEpisodesSelecteds(self):
        model = self.episodesTable.selectionModel()
        rows = model.selectedRows()
        rows.sort()
        for row in rows:
            pos = row.row()
            self.add2queue(None, pos)

    def getNewEpisodes(self):
        self.statusBar().showMessage(
            _translate('MainWindow', 'Searching new episodes....')
        )
        thread = db.updateEpisodes(self, self.podcastSelected, True)
        thread.newEpisodes.connect(self.updateEpisodesList)
        thread.end.connect(self.reloadPCList)
        thread.start()

    def updateEpisodesList(self, data):
        if self.podcastSelected != 0 and data:
            thread = addNewEpidodes(self, data)
            thread.episodes.connect(self.insertEpisode)
            thread.start()

        self.statusBar().showMessage('')
        self.podcastsList.repaint()

    def queueMenu(self, event):
        menu = QtWidgets.QMenu(self.queueList)
        delIcon = QIcon.fromTheme('list-remove')
        delAction = QtWidgets.QAction(
            delIcon,
            _translate('MainWindow', 'Remove from queue'),
            self
        )
        delAction.triggered.connect(self.getQueueSelecteds)
        menu.addAction(delAction)
        menu.popup(QCursor.pos())

    def getQueueSelecteds(self):
        model = self.queueList.selectionModel()
        rows = model.selectedRows()
        rows.sort()
        indexes = model.selectedIndexes()
        indexes.sort()
        items = [self.queueList.itemFromIndex(index) for index in indexes]
        for item in items:
            pos = self.queueList.row(item)
            self.queueList.removeItemWidget(item)
            self.queueList.model().removeRow(pos)
            self.player.delete(pos)

    def showConfDialog(self):
        dialog = conf.configDialog(self)
        dialog.exec()
        self.config = conf.getConf()
        self.reloadPCList(True)

    def podcastsMenu(self, event):
        menu = QtWidgets.QMenu(self.podcastsList)
        addIcon = QIcon.fromTheme('list-remove')
        addAction = QtWidgets.QAction(
            addIcon,
            _translate('MainWindow', 'Unsubscribe'),
            self
        )
        addAction.triggered.connect(self.unsubscribe)
        menu.addAction(addAction)
        menu.popup(QCursor.pos())

    def unsubscribe(self):
        model = self.podcastsList.selectionModel()
        rows = model.selectedRows()
        rows.sort()
        for row in rows:
            pos = row.row()
            item = self.podcastsList.item(pos)
            idPodcast = item.value
            if (idPodcast):
                remove = db.removePodcast(idPodcast)
                if remove:
                    self.podcastsList.model().removeRow(pos)
                    self.episodesTable.clear()
                    self.episodesTable.setRowCount(0)
                    self.podcastTitle.setText(
                        _translate('MainWindow', 'Podcast')
                    )
                    self.podcastWeb.setText(
                        _translate('MainWindow', 'Web')
                    )
                    self.podcastDesc.setText(
                        _translate('MainWindow', 'Description')
                    )
                    coverImage = QPixmap(':/img/icon.svg')
                    self.podcastCover.setPixmap(
                        coverImage.scaled(128, 128, Qt.KeepAspectRatio)
                    )

    def addDownload(self, pressed, pos=None):
        if not pos and pos != 0:
            source = self.sender()
            pos = source.value

        data = self.episodesData[pos]

        item = self.dw.add(self, data, self.player)
        myItem = QtWidgets.QListWidgetItem()
        self.downloadsList.addItem(myItem)
        self.downloadsList.setItemWidget(myItem, item)

        minimumSizeHint = self.downloadsList.minimumSizeHint()
        minimumSizeHint.setHeight(48)
        myItem.setSizeHint(minimumSizeHint)

    def addDownloads(self):
        """Add multiple downloads"""
        model = self.episodesTable.selectionModel()
        rows = model.selectedRows()
        rows.sort()
        for row in rows:
            pos = row.row()
            self.addDownload(None, pos)

    def dcPlayEpisode(self, w):
        row = w.row()
        self.player.queueData = []
        self.queueList.clear()
        self.player.queueList.clear()
        self.add2queue(None, row)
        self.player.startPlay()

    def changeEpisode(self, w):
        row = w.row()
        self.player.changePos(row)
        self.getEpisodeData(w)

    def paginationPrev(self, w):
        if self.currentPage > 0:
            self.currentPage -= 1
            self.getEpisodes()

    def paginationNext(self, w):
        if self.currentPage < self.totalPages - 1:
            self.currentPage += 1
            self.getEpisodes()

    def hideShowMW(self):
        if self.isMWShow:
            self.hide()
            self.isMWShow = False
        else:
            self.show()
            self.isMWShow = True

    def closeEvent(self, event):
        if ('disable_quit_dialog' in self.config and
                not self.config['disable_quit_dialog']):
            event.ignore()
            confirmClose.confirmDialog(self)

    def showAboutDialog(self):
        dialog = aboutDialog(self)
        dialog.exec()

    def import_opml(self):
        opmlfile, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            _translate('MainWindow', 'Select OPML file'),
            '',
            _translate('MainWindow', 'OPML (*.opml)'),
        )

        if opmlfile:
            import_thread = opml.import_subs(self, opmlfile)
            import_thread.end.connect(self.reloadPCList)
            import_thread.start()


class aboutDialog(QtWidgets.QDialog):
    """Show About dialog"""

    def __init__(self, parent=None):
        """ Init the class aboutDialog
            Parameters
            ----------
            parent : object, optional
                The MainWindow object (default is None)
        """
        super().__init__(parent)
        self.parent = parent
        self.ui = Ui_about.Ui_aboutDialog()
        self.ui.setupUi(self)

        curdir = os.path.dirname(os.path.abspath(__file__))
        license = os.path.join(curdir, 'LICENSE')
        with open(license) as f:
            self.ui.licenseText.setPlainText(f.read())


def init():
    LOCAL_DIR = path.dirname(path.realpath(__file__))
    app = QtWidgets.QApplication([])
    if not isLinux() and not isBSD():
        searchPaths = QIcon.fallbackSearchPaths()
        searchPaths.append(':/icons')
        QIcon.setFallbackSearchPaths(searchPaths)
        QIcon.setThemeName('breeze')

    defaultLocale = QLocale.system().name()
    if defaultLocale == 'es_ES':
        defaultLocale = 'es'

    translator = QTranslator()
    translator.load(LOCAL_DIR + "/locales/" + defaultLocale + ".qm")
    app.installTranslator(translator)
    window = MainWindow()
    window.retranslateUi(window)
    window.show()
    app.exec_()
