# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QThread
from .utils import (
    parseFeed,
    getAppDataDir,
    getAppCacheDir,
    downloadCover,
    coverExist
)
import time
import sqlite3
import urllib
import re
from datetime import datetime
from os import path
from shutil import copyfile
from pathlib import Path

db_dir = getAppDataDir()
cache_dir = getAppCacheDir()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class addPodcast(QThread):
    podcast = pyqtSignal(int, int)

    def __init__(self, parent, url):
        super(addPodcast, self).__init__(parent)
        self.url = url

    def run(self):
        con = sqlite3.connect(db_dir + "mpp.db")
        con.row_factory = dict_factory
        cursor = con.cursor()

        if not cursor:
            print("Database Error", "Unable To Connect To The Database!")
            self.stop()
        else:
            data = parseFeed(self.url)
            # Firts insert the podcasts info

            # Download the cover
            cover_name = data['cover_url'].split('/')[-1].split('?')[0]
            downloadCover(data['cover_url'], cover_name)

            insert = cursor.execute(
                """
                INSERT INTO podcasts (
                    title,
                    url,
                    cover,
                    description,
                    pageUrl,
                    coverUrl
                )
                VALUES (
                    '{0}',
                    '{1}',
                    '{2}',
                    '{3}',
                    '{4}',
                    '{5}')
                """.format(
                    data['title'],
                    self.url,
                    cover_name,
                    data['description'],
                    data['link'],
                    data['cover_url']
                )
            )
            con.commit()

            if not insert:
                self.podcast.emit(False)

            lastid = cursor.lastrowid
            episodes = []
            sql = """
                INSERT INTO episodes (
                    idPodcast,
                    title,
                    description,
                    url,
                    date,
                    totalTime
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
            """

            for e in data['episodes']:

                description = ''

                if 'description_html' in e:
                    description = e['description_html']
                else:
                    description = e['description']
                    description = re.sub(
                        r'(https?:\/\/[^\s]+)', r'<a href="\g<0>">\g<0></a>',
                        description
                    )

                episodeUrl = ''
                if (e['enclosures']):
                    episodeUrl = e['enclosures'][0]['url']
                else:
                    episodeUrl = e['link']

                episode = (
                    lastid,
                    e['title'],
                    description,
                    episodeUrl,
                    e['published'],
                    e['total_time']
                )

                episodes.append(episode)

            cursor.executemany(sql, episodes)
            con.commit()

            # Insert the last date in the podcast data for insert new episodes later
            cursor.execute(
                'UPDATE podcasts SET lastUpdate=%i WHERE idPodcast=%i' % (
                    episodes[0][4],
                    lastid
                )
            )
            con.commit()
            con.close()
            self.podcast.emit(lastid, len(episodes))

    def stop(self):
        self.quit()
        self.wait()


class getEpisodes(QThread):
    episodes = pyqtSignal(dict)

    def __init__(self, parent, idPodcast):
        super(getEpisodes, self).__init__(parent)
        self.idPodcast = idPodcast

    def run(self):
        con = sqlite3.connect(db_dir + "mpp.db")
        con.row_factory = dict_factory
        cursor = con.cursor()
        if not cursor:
            print("Database Error", "Unable To Connect To The Database!")
            self.stop()
        else:
            sql = """SELECT e.*, strftime('%d/%m/%Y',
            datetime(e.date, 'unixepoch', 'localtime')) AS date_format,
            p.title AS pc_title, p.cover
            FROM episodes e
            INNER JOIN podcasts p on p.idPodcast = e.idPodcast
            WHERE e.idPodcast = {0}
            ORDER BY e.date DESC""".format(self.idPodcast)

            cursor.execute(sql)
            rows = cursor.fetchall()
            con.close()

            for r in rows:
                totalTime = time.strftime(
                    '%H:%M:%S', time.gmtime(r['totalTime'])
                )
                r['totalTime'] = totalTime
                self.episodes.emit(r)

    def stop(self):
        self.quit()
        self.wait()


class getPodcasts(QThread):
    podcast = pyqtSignal(dict)

    def __init__(self, parent):
        super(getPodcasts, self).__init__(parent)

    def run(self):
        con = sqlite3.connect(db_dir + "mpp.db")
        con.row_factory = dict_factory
        cursor = con.cursor()
        if not cursor:
            print("Database Error", "Unable To Connect To The Database!")
            self.stop()
        else:
            cursor.execute("""
                SELECT p.*, COUNT(e.idEpisode) AS total_episodes
                FROM podcasts p
                INNER JOIN episodes e ON e.idPodcast = p.idPodcast
                GROUP BY p.idPodcast
            """)
            rows = cursor.fetchall()
            con.close()

            for r in rows:
                self.podcast.emit(r)

    def stop(self):
        self.quit()
        self.wait()


def getPodcast(idPodcast):
    con = sqlite3.connect(db_dir + "mpp.db")
    con.row_factory = dict_factory
    cursor = con.cursor()
    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False
    else:
        cursor.execute("""SELECT p.*, COUNT(e.idEpisode) AS total_episodes
                FROM podcasts p
                INNER JOIN episodes e ON e.idPodcast = p.idPodcast
                WHERE p.idPodcast = ?""", (idPodcast,))
        podcast = cursor.fetchone()
        con.close()
        return podcast


class updateEpisodes(QThread):
    newEpisodes = pyqtSignal(object)
    end = pyqtSignal(bool)

    def __init__(self, parent, idPodcast=None, returnNew=False):
        super(updateEpisodes, self).__init__(parent)
        self.idPodcast = idPodcast
        self.returnNew = returnNew

    def run(self):
        con = sqlite3.connect(db_dir + "mpp.db")
        con.row_factory = dict_factory
        cursor = con.cursor()
        dataReturn = []
        refreshList = False

        if not cursor:
            print("Database Error", "Unable To Connect To The Database!")
            self.stop()
        else:
            sql = """
                SELECT idPodcast, url, lastUpdate, title, cover, coverUrl
                FROM podcasts
            """
            if self.idPodcast and not self.returnNew:
                sql += ' WHERE idPodcast=%i' % self.idPodcast

            cursor.execute(sql)
            podcasts = cursor.fetchall()

            for p in podcasts:
                try:
                    episodes = []

                    data = parseFeed(p['url'])
                    if not data:
                        continue

                    sql = """
                        INSERT INTO episodes (
                            idPodcast,
                            title,
                            description,
                            url,
                            date,
                            totalTime
                        ) VALUES (
                            ?,
                            ?,
                            ?,
                            ?,
                            ?,
                            ?
                        )
                    """

                    cover_name = data['cover_url'].split('/')[-1].split('?')[0]
                    if not p['coverUrl'] or not coverExist(cover_name):
                        downloadCover(
                            data['cover_url'],
                            cache_dir+'/'+cover_name
                        )
                        refreshList = True

                    for e in data['episodes']:
                        published = int(e['published'])
                        if published <= p['lastUpdate']:
                            break

                        description = ''

                        if 'description_html' in e:
                            description = e['description_html']
                        else:
                            description = e['description']
                            description = re.sub(
                                r'(https?:\/\/[^\s]+)',
                                r'<a href="\g<0>">\g<0></a>',
                                description
                            )

                        episodeUrl = ''
                        if (e['enclosures']):
                            episodeUrl = e['enclosures'][0]['url']
                        else:
                            episodeUrl = e['link']

                        episode = (
                            p['idPodcast'],
                            e['title'],
                            description,
                            episodeUrl,
                            e['published'],
                            e['total_time']
                        )

                        episodes.append(episode)

                        if self.returnNew:
                            date_format = datetime.utcfromtimestamp(
                                e['published']
                            ).strftime('%d/%m/%Y a las %H:%M')

                            new = {
                                'idPodcast': p['idPodcast'],
                                'title': e['title'],
                                'description': description,
                                'episodeUrl': episodeUrl,
                                'date_format': date_format,
                                'totalTime': e['total_time'],
                                'pc_title': p['title'],
                                'cover': p['cover'],
                                'url': episodeUrl
                            }
                            dataReturn.append(new)

                    if len(episodes) > 0:
                        cursor.executemany(sql, episodes)
                        con.commit()
                        # Insert the last date in the podcast data for insert new episodes later
                        cursor.execute("""
                            UPDATE podcasts
                            SET lastUpdate=%i, coverUrl='%s'
                            WHERE idPodcast=%i
                            """ % (
                                episodes[0][4],
                                data['cover_url'],
                                p['idPodcast'])
                            )
                        con.commit()

                        if self.idPodcast and self.returnNew and (self.idPodcast == p['idPodcast']):
                            dataReturn.reverse()
                            self.newEpisodes.emit(dataReturn)
                except urllib.error.HTTPError:
                    continue

        con.close()
        self.newEpisodes.emit(dataReturn)
        self.end.emit(refreshList)

    def stop(self):
        self.quit()
        self.wait()


def getEpisode(idEpisode):
    con = sqlite3.connect(db_dir + "mpp.db")
    con.row_factory = dict_factory
    cursor = con.cursor()
    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False
    else:
        cursor.execute("""SELECT *
                FROM episodes
                WHERE idEpisode = ?""", (idEpisode,))
        podcast = cursor.fetchone()
        con.close()
        return podcast


def createDB():
    con = sqlite3.connect(db_dir + "mpp.db")
    cursor = con.cursor()

    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False
    else:
        dir = path.dirname(path.realpath(__file__))
        with open(dir + '/ddbb.sql') as sqlfile:
            sql = sqlfile.read()
            cursor.executescript(sql)


def updateDB():
    """Update the database tables"""

    # Make a ddbb.sql backcup
    copyfile(db_dir + 'mpp.db', db_dir + 'mpp.db.bck')
    con = sqlite3.connect(db_dir + "mpp.db")
    con.row_factory = dict_factory
    cursor = con.cursor()

    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False
    else:
        # First check if one of the new columns exists

        cursor.execute("""
            SELECT COUNT(*) AS CNTREC FROM pragma_table_info('podcasts') WHERE name='coverUrl'
        """)

        check = cursor.fetchone()
        if check['CNTREC'] > 0:
            delete_file = Path(db_dir + 'mpp.db.bck')
            delete_file.unlink()
            con.close()
            return
        
        # Rename the tables for after copy the data
        con.execute('ALTER TABLE podcasts RENAME TO podcasts_bck')
        con.commit()
        con.execute('ALTER TABLE episodes RENAME TO episodes_bck')
        con.commit()

        # Now create again the tables
        dir = path.dirname(path.realpath(__file__))
        with open(dir + '/ddbb.sql') as sqlfile:
            sql = sqlfile.read()
            cursor.executescript(sql)

            # Get the columns name to copy the data
            cursor.execute("SELECT name FROM pragma_table_info('podcasts_bck')")
            insert = 'INSERT INTO podcasts ('
            columns = cursor.fetchall()
            for i in range(len(columns)):
                col = columns[i]['name']
                if i > 0:
                    insert += ','
                insert += col

            insert += ') SELECT * FROM podcasts_bck'
            cursor.execute(insert)
            con.commit()

            # The same for the episodes
            cursor.execute("SELECT name FROM pragma_table_info('episodes_bck')")
            insert = 'INSERT INTO episodes ('
            columns = cursor.fetchall()
            for i in range(len(columns)):
                col = columns[i]['name']
                if i > 0:
                    insert += ','
                insert += col

            insert += ') SELECT * FROM episodes_bck'
            cursor.execute(insert)
            con.commit()

            # Add coverUrl data on podcasts:
            cursor.execute("SELECT idPodcast, url FROM podcasts")
            rows = cursor.fetchall()

            for r in rows:
                data = parseFeed(r['url'])
                cover_name = data['cover_url'].split('/')[-1].split('?')[0]
                downloadCover(data['cover_url'], cover_name)
                cursor.execute(
                    "UPDATE podcasts set coverUrl='{}' WHERE idPodcast={}"
                    .format(data['cover_url'], r['idPodcast'])
                )
                con.commit()
                
            # Finally remove thec _bck tables and close db
            cursor.execute('DROP TABLE podcasts_bck')
            cursor.execute('DROP TABLE episodes_bck')
            con.commit()
            con.close()


def removePodcast(idPodcast):
    con = sqlite3.connect(db_dir + "mpp.db")
    cursor = con.cursor()
    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False

    try:
        cursor.execute('DELETE FROM podcasts WHERE idPodcast=?', (idPodcast,))
        con.commit()
        cursor.execute('DELETE FROM episodes WHERE idPodcast=?', (idPodcast,))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as err:
        print(err)
        return False


def addDownLocalfile(idEpisode, localfile):
    con = sqlite3.connect(db_dir + "mpp.db")
    cursor = con.cursor()
    if not cursor:
        print("Database Error", "Unable To Connect To The Database!")
        return False

    try:
        cursor.execute('UPDATE episodes SET localfile=? WHERE idEpisode=?', (localfile, idEpisode))
        con.commit()
        con.close()
        return True
    except sqlite3.Error as err:
        print(err)
        return False
