import os
import re
import sys
import glob
import sqlite3
import datetime
import argparse
import pathlib
import hashlib
import requests
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from . import setting


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
    Parameters
    ----------
    text: str
        ホロジュールのHTMLソースコード
    year: int
        ホロジュールには年情報が含まれていないため、メタ情報として渡す必要がある。

    Returns
    -------
    streams: list[Stream]
    """
    streams = []

    soup = BeautifulSoup(text, 'html.parser')

    updated_at = datetime.datetime.now()

    month = None
    day = None
    for container in soup.select('.tab-pane > .container'):

        # 日付バーから日付を取り出す
        date_headers = container.select('.navbar-text')
        if date_headers:
            date_text = date_headers[0].get_text(strip=True)

            m = re.search(r'^(\d+)/(\d+)\s*\((.+)\)$', date_text)
            month = int(m.group(1))
            day = int(m.group(2))
            # day_of_week_ja = m.group(3)

        # 配信情報からURL等を取り出す
        thumbnails = container.select('a.thumbnail')
        if thumbnails:
            # 配信情報よりも前に日付バーがあることを期待する
            # (そうでないと配信日が判らない)
            assert month is not None
            assert day is not None

            for thumb in thumbnails:
                stream_url = thumb['href']

                # a.thumbnailの下にdivが無い場合はカルーセルと判定する
                if thumb.div is None:
                    print('[DEBUG] it is a carousel')
                    continue

                rows = thumb.div.div.find_all('div', recursive=False)

                time_text = rows[0].div.find_all('div', recursive=False)[0].get_text(strip=True)
                if not time_text:
                    # 時刻無しは広告と判定する
                    continue

                m = re.search(r'^(\d+):(\d+)$', time_text)
                hours = int(m.group(1))
                minutes = int(m.group(2))

                starts_at = datetime.datetime(year, month, day, hours, minutes)

                streamer_name = rows[0].div.find_all('div', recursive=False)[1].get_text(strip=True)

                thumb_url = rows[1].img['src']

                icon_urls = []
                for icon in rows[2].div.find_all('div', recursive=False):
                    icon_urls.append(icon.img['src'])

                streamer_icon_url = icon_urls[0] if icon_urls else None

                streamer = Streamer(streamer_name, streamer_icon_url)
                stream = Stream(stream_url, streamer, thumb_url, starts_at, updated_at)
                streams.append(stream)

    return streams


def escape_as_sqlite_str(s):
    return "'{}'".format(s.replace("'", "''"))


def parse(indir, dbpath, thumb_dir, fresh=False, verbose=False):
    # htmlを解析
    print('parsing htmls ...', file=sys.stderr)
    start = datetime.datetime.now()

    htmlpaths = sorted(glob.glob(os.path.join(indir, '*.html')))
    print('number of htmls: ', len(htmlpaths), file=sys.stderr)

    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    # 未登録のファイルのパース済みフラグをクリアする
    cur.execute('''CREATE TABLE IF NOT EXISTS htmlfiles(
                    filename   TEXT PRIMARY KEY,
                    is_parsed  INTEGER NOT NULL
            );''')

    for htmlpath in htmlpaths:
        cur.execute('''INSERT OR IGNORE INTO htmlfiles VALUES(
                {}, {}
                );'''.format(escape_as_sqlite_str(os.path.basename(htmlpath)), 0))

    streams = []
    streamers = []

    for htmlpath in htmlpaths:

        # パース済みのファイルをスキップする
        cur.execute('''SELECT is_parsed FROM htmlfiles WHERE filename = {}
                ;'''.format(escape_as_sqlite_str(os.path.basename(htmlpath))))

        is_parsed = cur.fetchone()[0]
        if is_parsed and not fresh:
            if verbose:
                print(f'skip {htmlpath}', file=sys.stderr)
            continue

        # ファイルをパースする
        print(f'parsing {htmlpath} ...', file=sys.stderr)

        year = int(os.path.basename(htmlpath)[:4])

        with open(htmlpath, encoding='UTF-8') as f:
            streams.extend(parse_holodule(f.read(), year))

        for stream in streams:
            streamers.append(stream.streamer)

        # パース済みフラグをセットする
        cur.execute('''UPDATE htmlfiles
                SET is_parsed = 1
                WHERE filename = {}
                ;'''.format(escape_as_sqlite_str(os.path.basename(htmlpath))))

    streamers = sorted(set(streamers))

    elapsed_time = datetime.datetime.now() - start
    print(f'parse time: {elapsed_time} [sec]', file=sys.stderr)

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

    cur.execute('''CREATE TABLE IF NOT EXISTS thumbnails(
                    url           TEXT NOT NULL,
                    hash          TEXT NOT NULL,
                    filename      TEXT NOT NULL,
                    PRIMARY KEY(url, hash)
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

    print('downloading thumbnails ...', file=sys.stderr)
    start = datetime.datetime.now()

    if not os.path.exists(thumb_dir):
        print(f'create directory {thumb_dir}', file=sys.stderr)
        os.mkdir(thumb_dir)

    # not_found_image_sha256 = '20e9aab22032d85684d7d916a1013f7c577a132a5b10ea3fd3578e8d0b28a711'
    for i, stream in enumerate(streams):
        # サムネイルをダウンロードする
        print(f'downloading {stream.thumb_url} ... ({i+1}/{len(streams)})', file=sys.stderr)
        r = requests.get(stream.thumb_url)
        hash = hashlib.sha256(r.content).hexdigest()

        # サムネイルが登録済みならスキップする
        #cur.execute('''SELECT COUNT(*) FROM thumbnails WHERE url = {} AND hash = {}
        #        ;'''.format(escape_as_sqlite_str(stream.thumb_url),
        #                    escape_as_sqlite_str(hash)))
        #
        #count = cur.fetchone()[0]
        #if count >= 1:
        #    continue

        # サムネイルをファイルに保存する
        stream_id = parse_qs(urlparse(stream.url).query)['v'][0]
        short_hash = hash[:7]
        ext = pathlib.Path(stream.thumb_url).suffix
        savename = f'{stream_id}_{short_hash}{ext}'
        savepath = pathlib.Path(thumb_dir) / savename

        if savepath.exists():
            if verbose:
                print(f'skip {savepath}', file=sys.stderr)
        else:
            with open(str(savepath), 'wb') as f:
                f.write(r.content)
            print(f'write {savepath}', file=sys.stderr)

        # サムネイルを登録する
        cur.execute('''INSERT OR REPLACE INTO thumbnails VALUES(
                {}, {}, {}
                );'''.format(escape_as_sqlite_str(stream.thumb_url),
                             escape_as_sqlite_str(hash),
                             escape_as_sqlite_str(savename)))

    elapsed_time = datetime.datetime.now() - start
    print(f'download time: {elapsed_time} [sec]', file=sys.stderr)

    conn.commit()
    conn.close()

    print(f'write {dbpath}', file=sys.stderr)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-I', '--indir', help='The directory that contains html files')
    argparser.add_argument('-d', '--dbpath')
    argparser.add_argument('-t', '--thumbdir', help='The directory that contains thumbnails of streams')
    argparser.add_argument('-f', '--fresh', action='store_true')
    argparser.add_argument('-v', '--verbose', action='store_true')
    args = argparser.parse_args()

    indir = os.path.abspath(str(args.indir or setting.holodule_dir))
    dbpath = os.path.abspath(str(args.dbpath or setting.dbname))
    thumb_dir = os.path.abspath(str(args.thumbdir or setting.thumb_dir))

    parse(indir, dbpath, thumb_dir, fresh=args.fresh, verbose=args.verbose)
    return 0


if __name__ == '__main__':
    status = main()
    if status != 0:
        sys.exit(status)
