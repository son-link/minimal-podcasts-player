from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from PyQt5.QtCore import QUrl, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap
from .utils import ms_to_time

_translate = QCoreApplication.translate


class Player(QMediaPlayer):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent)
        self.parent = parent
        self.player = QMediaPlayer()
        self.queueList = QMediaPlaylist()
        self.player.setPlaylist(self.queueList)
        self.queueData = []
        self.position = 0
        self.volume = 100

        self.player.mediaStatusChanged.connect(self.qmp_mediaStatusChanged)
        self.player.positionChanged.connect(self.qmp_positionChanged)
        self.player.durationChanged.connect(self.durationChanged)
        self.queueList.currentIndexChanged.connect(self.playlistPosChanged)

    def add(self, data):
        """Add track to the queue"""
        queueData = {
            'idEpisode': data['idEpisode'],
            'pc_title': data['pc_title'],
            'title': data['title'],
            'url': data['url'],
            'date': data['date_format'],
            'description': data['description'],
            'localfile': data['localfile']
        }
        url = data['url']
        if data['localfile']:
            url = 'file://' + data['localfile']

        self.queueData.append(queueData)
        self.queueList.addMedia(QMediaContent(QUrl(url)))
        self.parent.playBtn.setEnabled(True)
        self.parent.stopBtn.setEnabled(True)
        self.parent.back10Btn.setEnabled(True)
        self.parent.for10Btn.setEnabled(True)
        self.parent.timeSlider.setEnabled(True)

    def playPause(self):
        icon = QIcon.fromTheme("media-playback-pause")

        if self.player.state() == QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                if self.queueList.mediaCount() != 0:
                    self.player.play()
            elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.queueList.setCurrentIndex(self.position)
                self.player.play()
            elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.player.play()
        elif self.player.state() == QMediaPlayer.PlayingState:
            icon = QIcon.fromTheme("media-playback-start")
            self.player.pause()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()

        self.parent.playBtn.setIcon(icon)

    def startPlay(self):
        data = self.queueData[0]
        self.queueList.setCurrentIndex(0)
        self.parent.curPCLabel.setText(data['pc_title'])
        self.parent.curTrackName.setText(data['title'])
        self.player.play()
        icon = QIcon.fromTheme("media-playback-pause")
        self.parent.playBtn.setIcon(icon)

    def stop(self):
        self.player.stop()
        icon = QIcon.fromTheme("media-playback-start")
        self.parent.playBtn.setIcon(icon)

    def setPosition(self, pos):
        self.player.setPosition(pos)

    def durationChanged(self, duration):
        total_time = '0:00:00'
        duration = self.player.duration()
        total_time = ms_to_time(duration)
        self.parent.timeSlider.setMaximum(duration)
        self.currentTrackDuration = duration
        self.parent.totalTimeLabel.setText(total_time)

    def qmp_mediaStatusChanged(self, status):
        icon = QIcon.fromTheme("media-playback-pause")
        if self.player.state() == QMediaPlayer.StoppedState:
            icon = QIcon.fromTheme("media-playback-start")
        elif self.player.state() == QMediaPlayer.PausedState:
            icon = QIcon.fromTheme("media-playback-start")

        self.parent.playBtn.setIcon(icon)

    def qmp_positionChanged(self, position, senderType=False):
        self.currentTime = position
        current_time = '0:00:00'

        if position != -1:
            current_time = ms_to_time(position)
            self.parent.timeLabel.setText(current_time)

        self.parent.timeSlider.blockSignals(True)
        self.parent.timeSlider.setValue(position)
        self.parent.timeSlider.blockSignals(False)

    def playlistPosChanged(self):
        if self.queueList.mediaCount() > 0:
            pos = self.queueList.currentIndex()
            data = self.queueData[pos]
            self.parent.curPCLabel.setText(data['pc_title'])
            self.parent.curTrackName.setText(data['title'])
            windowTitle = '{0} - {1}'.format(data['pc_title'], data['title'])
            self.parent.setWindowTitle(windowTitle)
            if self.queueList.mediaCount() > 1:
                if pos < self.queueList.mediaCount() - 1:
                    self.parent.queueNextBtn.setEnabled(True)
                else:
                    self.parent.queueNextBtn.setEnabled(False)

                if pos > 0:
                    self.parent.queuePrevBtn.setEnabled(True)
                else:
                    self.parent.queuePrevBtn.setEnabled(False)

                if pos < self.queueList.mediaCount():
                    prevPos = 0
                    if self.position < pos:
                        prevPos = pos - 1
                    else:
                        prevPos = pos + 1
                    prevItem = self.parent.queueList.item(prevPos)
                    prevWidget = self.parent.queueList.itemWidget(prevItem)
                    if prevItem:
                        prevWidget.statusIcon.setPixmap(QPixmap())

            self.position = pos
            item = self.parent.queueList.item(pos)
            widget = self.parent.queueList.itemWidget(item)
            if widget:
                icon = QIcon.fromTheme("media-playback-start")
                widget.statusIcon.setPixmap(icon.pixmap(16, 16))

    def setVolume(self, volume):
        self.player.setVolume(volume)

    def rev10Secs(self):
        position = self.player.position()
        new_pos = position - 10000
        self.player.setPosition(new_pos)

    def for10Secs(self):
        position = self.player.position()
        new_pos = position + 10000
        self.player.setPosition(new_pos)

    def delete(self, position):
        """ Delete the track and her data from position"""
        self.queueData.pop(position)
        self.queueList.removeMedia(position)
        if self.queueList.mediaCount() > 0:
            if position == self.position:
                self.playlistPosChanged()
        else:
            self.parent.setWindowTitle('Minimal Podcasts Player')
            self.parent.infoEpisodeLabel.setText('')
            self.parent.curPCLabel.setText(_translate("MainWindow", "Podcast"))
            self.parent.curTrackName.setText(_translate("MainWindow", "Episode Title"))
            self.parent.queuePrevBtn.setEnabled(False)
            self.parent.queueNextBtn.setEnabled(False)
            self.parent.playBtn.setEnabled(False)
            self.parent.stopBtn.setEnabled(False)
            self.parent.back10Btn.setEnabled(False)
            self.parent.for10Btn.setEnabled(False)
            self.parent.timeSlider.setEnabled(False)

    def changeUrl(self, idEpisode, url):
        pos = next((i for i, item in enumerate(self.queueData) if item['idEpisode'] == idEpisode), None)
        if (pos):
            self.queueData[pos]['url'] = url
            self.queueList.removeMedia(pos)
            self.queueList.insertMedia(pos, QMediaContent(QUrl(url)))
