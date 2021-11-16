from opyml import OPML, Outline
from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    QCoreApplication,
    pyqtSignal,
    QThread,
    QVariant
)
from .utils import verifyFeed, getAppDataDir
from . import db
import sqlite3

_translate = QCoreApplication.translate
db_dir = getAppDataDir()


class import_subs(QThread):
    end = pyqtSignal(bool)

    def __init__(self, parent, opmlfile):
        super().__init__(parent)
        self.parent = parent
        self.subscription = []
        self.opmlfile = opmlfile

    def run(self):
        if self.opmlfile:
            with open(self.opmlfile) as f:
                document = OPML.from_xml(f.read())
                for outline in document.body.outlines:
                    if outline.type == 'folder':
                        self.folder(outline)
                    else:
                        self.subscription.append(outline.xml_url)

                if len(self.subscription) > 0:
                    self.parent.statusBar().showMessage(
                        _translate(
                            'opml',
                            'Importing subscription(s)'
                        )
                    )

                    for url in self.subscription:
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
                self.subscription.append(line.xml_url)


class export_subs(QThread):
    step = pyqtSignal(int)
    end = pyqtSignal(bool)

    def __init__(self, parent, opmlfile):
        super().__init__(parent)
        self.parent = parent
        self.opmlfile = opmlfile
        self.document = OPML()

    def run(self):
        if self.opmlfile:
            con = sqlite3.connect(db_dir + "mpp.db")
            con.row_factory = db.dict_factory
            cursor = con.cursor()
            if not cursor:
                print("Database Error", "Unable To Connect To The Database!")
                self.end.emit(False)
            else:
                cursor.execute("""
                    SELECT title, url, pageURL, description FROM podcasts
                """)
                rows = cursor.fetchall()
                con.close()

                for r in rows:
                    self.document.body.outlines.append(
                        Outline(
                            text=r['title'],
                            title=r['title'],
                            description=r['description'],
                            xml_url=r['url'],
                            url=r['pageUrl']
                        )
                    )
                    with open(self.opmlfile, 'w') as f:
                        f.write(self.document.to_xml())
                        f.close()
