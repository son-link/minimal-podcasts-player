import podcastparser
from urllib.request import urlopen, Request, HTTPError, URLError
from PyQt5.QtCore import pyqtSignal, QThread, QVariant
from os import getenv, path
import pathlib
import platform
import urllib


def parseFeed(url):
    """
    docstring
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as response:
        try:
            return podcastparser.parse(url, response)
        except podcastparser.FeedParseError:
            return False
        except HTTPError:
            return False
        except URLError:
            return False


def ms_to_time(t):
    '''
    Convert nanoseconds to hours, minutes and seconds
    '''
    s, ns = divmod(t, 1000)
    m, s = divmod(s, 60)

    if m < 60:
        return "0:%02i:%02i" % (m, s)
    else:
        h, m = divmod(m, 60)
        return "%i:%02i:%02i" % (h, m, s)


class updatePodcasts(QThread):
    data = pyqtSignal(QVariant)

    def __init__(self, parent, url):
        super(updatePodcasts, self).__init__(parent)
        self.url = url

    def run(self):
        data = parseFeed(self.url)
        self.data.emit(data)


class addNewEpidodes(QThread):
    episodes = pyqtSignal(QVariant, bool)

    def __init__(self, parent=None, data=None):
        super(addNewEpidodes, self).__init__(parent)
        self.data = data

    def run(self):
        for d in self.data:
            self.episodes.emit(d, True)

    def stop(self):
        self.quit()
        self.wait()


def getAppDataDir():
    """Return the O.S. default user appdata dir"""

    path = ''
    if getenv('HOME'):
        path = getenv('HOME') + '/.local/share/mpp/'  # Linux
    elif getenv('APPDATA'):
        path = getenv('APPDATA') + '\\mpp\\'  # Windows

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path


def getAppCacheDir():
    """Return the O.S. default user cache dir"""

    path = ''
    if getenv('HOME'):
        path = getenv('HOME') + '/.cache/mpp/'  # Linux
    elif getenv('APPDATA'):
        path = getenv('APPDATA') + '\\mpp\\cache'  # Windows

    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path


def isLinux():
    """Return True if the platform is Linux and not the AppImage"""
    if platform.system() == 'Linux' and not getenv('APPIMAGE'):
        return True
    else:
        return False


def isBSD():
    """Return True if the platform is FreeBSD"""
    if platform.system() == 'FreeBSD':
        return True
    else:
        return False


def isWindows():
    """Return True if the platform is Windows"""
    if platform.system() == 'Windows':
        return True
    else:
        return False


def downloadCover(url, filename):
    "Download the cover"
    cover = path.join(getAppCacheDir(), filename)
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'Mozilla/5.0')
    filename, headers = opener.retrieve(url, cover)


def coverExist(filename):
    """ Check if the podcast cover exists, if not, download it again"""
    cover = path.join(getAppCacheDir(), filename)

    if not path.exists(cover):
        return False

    return True
