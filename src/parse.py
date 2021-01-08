import os
import re
import sys
import glob
import sqlite3
import datetime
import argparse
from bs4 import BeautifulSoup
from .setting import holodule_dir, dbname


class Streamer():
    def __init__(self, name, icon_path=None):
        self.name = name
        self.icon_path = icon_path

    def __str__(self):
        return self.name

    def __key(self):
        return tuple(self.__dict__.values())

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        return self.__key() < other.__key()


class Stream:
    def __init__(self, url, streamer, thumb_url, starts_at, updated_at):
        self.url = url
        self.streamer = streamer
        self.thumb_url = thumb_url
        self.starts_at = starts_at
        self.updated_at = updated_at

    def __str__(self):
        return '{} {} {}'.format(self.starts_at.strftime('%Y/%m/%d %H:%M:%S'), self.streamer, self.url)

    def __key(self):
        return (self.__dict__.values())

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        return self.__key() < other.__key()


def parse_holodule(text, year):
    """
    ホロジュールには年情報が含まれていないため、メタ情報として渡す必要がある。
    """
    streams = []

    soup = BeautifulSoup(text, 'html.parser')

    updated_at = datetime.datetime.now()

    month = None
    day_of_month = None
    for container in soup.select('.tab-pane > .container'):

        date_headers = container.select('.navbar-text')
        if date_headers:
            date_text = date_headers[0].get_text(strip=True)

            m = re.search(r'^(\d+)/(\d+)\s*\((.+)\)$', date_text)
            month = int(m.group(1))
            day_of_month = int(m.group(2))
            #day_of_week_ja = m.group(3)

            #print('-- {}/{}({}) --'.format(month, day_of_month, day_of_week_ja))

        thumbnails = container.select('a.thumbnail')
        if thumbnails:
            for thumb in thumbnails:
                stream_url = thumb['href']

                rows = thumb.div.div.find_all('div', recursive=False)

                time_text = rows[0].div.find_all('div', recursive=False)[0].get_text(strip=True)
                if not time_text:
                    # 時刻無しは広告と判定する
                    continue

                m = re.search(r'^(\d+):(\d+)$', time_text)
                hours = int(m.group(1))
                minutes = int(m.group(2))

                starts_at = datetime.datetime(year, month, day_of_month, hours, minutes)

                streamer_name = rows[0].div.find_all('div', recursive=False)[1].get_text(strip=True)

                thumb_url = rows[1].img['src']

                icon_urls = []
                for icon in rows[2].div.find_all('div', recursive=False):
                    icon_urls.append(icon.img['src'])

                streamer_icon_url = icon_urls[0] if icon_urls else None

                #print('{} {} {}'.format(starts_at.strftime('%Y/%m/%d %H:%M:%S'), streamer_name, stream_url))

                streamer = Streamer(streamer_name, streamer_icon_url)
                stream = Stream(stream_url, streamer, thumb_url, starts_at, updated_at)
                streams.append(stream)

    return streams


def escape_as_sqlite_str(s):
    return "'{}'".format(s.replace("'", "''"))


def parse(fresh=False):
    # htmlを解析
    start = datetime.datetime.now()

    htmlfiles = sorted(glob.glob(os.path.join(holodule_dir, '*.html')))
    print('file count:', len(htmlfiles))

    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS htmlfiles(
                    filename   TEXT PRIMARY KEY,
                    is_parsed  INTEGER NOT NULL
            );''')

    for file_ in htmlfiles:
        cur.execute('''INSERT OR IGNORE INTO htmlfiles VALUES(
                {}, {}
                );'''.format(escape_as_sqlite_str(os.path.basename(file_)), 0))

    streams = []
    streamers = []

    for file_ in htmlfiles:

        cur.execute('''SELECT is_parsed FROM htmlfiles WHERE filename = {}
                ;'''.format(escape_as_sqlite_str(os.path.basename(file_))))

        is_parsed = cur.fetchone()[0]

        if not fresh and is_parsed:
            print('{}: skipped'.format(file_))
            continue

        print('{}: parsing...'.format(file_))

        year = int(os.path.basename(file_)[:4])

        with open(file_, encoding='UTF-8') as f:
            streams.extend(parse_holodule(f.read(), year))

        for stream in streams:
            streamers.append(stream.streamer)

        cur.execute('''UPDATE htmlfiles
                SET is_parsed = 1
                WHERE filename = {}
                ;'''.format(escape_as_sqlite_str(os.path.basename(file_))))

    streamers = sorted(set(streamers))

    elapsed_time = datetime.datetime.now() - start
    print('parse: {} [sec]'.format(elapsed_time))

    # 永続化

    cur.execute('''CREATE TABLE IF NOT EXISTS streams(
                    url           TEXT PRIMARY KEY,
                    thumb_url     TEXT NOT NULL,
                    streamer_name TEXT NOT NULL,
                    starts_at     TEXT,
                    updated_at    TEXT
            );''')

    cur.execute('''CREATE TABLE IF NOT EXISTS streamers(
                    name       TEXT PRIMARY KEY,
                    icon_path  TEXT
            );''')

    for stream in streams:
        cur.execute('''INSERT OR REPLACE INTO streams VALUES(
                {}, {}, {}, {}, {}
                );'''.format(escape_as_sqlite_str(stream.url),
                escape_as_sqlite_str(stream.thumb_url),
                escape_as_sqlite_str(stream.streamer.name),
                escape_as_sqlite_str(stream.starts_at.isoformat()),
                escape_as_sqlite_str(stream.updated_at.isoformat())))

    for streamer in streamers:
        cur.execute('''INSERT OR REPLACE INTO streamers VALUES(
                {}, {}
                );'''.format(escape_as_sqlite_str(streamer.name), escape_as_sqlite_str(streamer.icon_path)))

    conn.commit()
    conn.close()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--fresh', action='store_true')
    args = argparser.parse_args()

    parse(args.fresh)
    return 0


if __name__ == '__main__':
    status = main()
    if status != 0:
        sys.exit(status)
