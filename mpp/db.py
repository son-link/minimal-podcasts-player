# -*- coding: utf-8 -*-
from PyQt5.QtCore import pyqtSignal, QThread, QVariant
from .utils import parseFeed, getAppDataDir, getAppCacheDir
import time
import sqlite3
import urllib
import re
from datetime import datetime
from os import path

db_dir = getAppDataDir()
cache_dir = getAppCacheDir()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class addPodcast(QThread):
    podcast = pyqtSignal(QVariant)

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
            cover_name = data['cover_url'].split('/')[-1]
            file_name, headers = urllib.request.urlretrieve(data['cover_url'], cache_dir+'/'+cover_name)

            insert = cursor.execute("""
            INSERT INTO podcasts (title, url, cover, description, pageUrl)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(data['title'], self.url, cover_name, data['description'], data['link']))
            con.commit()

            if not insert:
                self.podcast.emit(False)

            lastid = cursor.lastrowid
            episodes = []
            sql = "INSERT INTO episodes (idPodcast, title, description, url, date, totalTime) VALUES (?, ?, ?, ?, ?, ?)"

            for e in data['episodes']:

                description = ''

                if 'description_html' in e:
                    description = e['description_html']
                else:
                    description = e['description']
                    description = re.sub('(https?:\/\/[^\s]+)', '<a href="\g<0>">\g<0></a>', description)

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
            cursor.execute('UPDATE podcasts SET lastUpdate=%i WHERE idPodcast=%i' % (episodes[0][4], lastid))
            con.commit()
            con.close()
            self.podcast.emit(lastid)

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
                totalTime = time.strftime('%H:%M:%S', time.gmtime(r['totalTime']))
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

    def __init__(self, parent, idPodcast=None, returnNew=False):
        super(updateEpisodes, self).__init__(parent)
        self.idPodcast = idPodcast
        self.returnNew = returnNew

    def run(self):
        con = sqlite3.connect(db_dir + "mpp.db")
        con.row_factory = dict_factory
        cursor = con.cursor()
        dataReturn = []

        if not cursor:
            print("Database Error", "Unable To Connect To The Database!")
            self.stop()
        else:
            sql = "SELECT idPodcast, url, lastUpdate, title, cover FROM podcasts"
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

                    sql = "INSERT INTO episodes (idPodcast, title, description, url, date, totalTime) VALUES (?, ?, ?, ?, ?, ?)"

                    for e in data['episodes']:
                        published = int(e['published'])
                        if published <= p['lastUpdate']:
                            break

                        description = ''

                        if 'description_html' in e:
                            description = e['description_html']
                        else:
                            description = e['description']
                            description = re.sub('(https?:\/\/[^\s]+)', '<a href="\g<0>">\g<0></a>', description)

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
                            date_format = datetime.utcfromtimestamp(e['published']).strftime('%d/%m/%Y a las %H:%M')
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
                        cursor.execute('UPDATE podcasts SET lastUpdate=%i WHERE idPodcast=%i' % (episodes[0][4], p['idPodcast']))
                        con.commit()

                        if self.idPodcast and self.returnNew and (self.idPodcast == p['idPodcast']):
                            dataReturn.reverse()
                            self.newEpisodes.emit(dataReturn)
                except urllib.error.HTTPError:
                    continue

        con.close()
        self.newEpisodes.emit(dataReturn)

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
