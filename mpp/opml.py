from opyml import OPML, Outline
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    QCoreApplication,
    pyqtSignal,
    QThread,
    QVariant,
    Qt
)
from .utils import verifyFeed
from . import db

_translate = QCoreApplication.translate


class import_subs(QThread):
    end = pyqtSignal(bool)

    def __init__(self, parent, opmlfile):
        super().__init__(parent)
        self.parent = parent
        self.suscriptions = []
        self.opmlfile = opmlfile

    def run(self):
        if self.opmlfile:
            with open(self.opmlfile) as f:
                document = OPML.from_xml(f.read())
                for outline in document.body.outlines:
                    if outline.type == 'folder':
                        self.folder(outline)
                    else:
                        self.suscriptions.append(outline.xml_url)

                if len(self.suscriptions) > 0:
                    self.parent.statusBar().showMessage(
                        'Import suscription(s)'
                    )

                    for url in self.suscriptions:
                        data = verifyFeed(url)
                        if data:
                            db.insertPodcast(url, data)
                    self.parent.statusBar().showMessage('')
                    self.end.emit(True)

    def folder(self, outline):
        for line in outline.outlines:
            if line.type == 'folder':
                self.folder(line)
            else:
                self.suscriptions.append(line.xml_url)
