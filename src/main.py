import os
import re
import sys
import sqlite3
import datetime
import requests
from bs4 import BeautifulSoup


class Streamer:
    def __init__(self, name, icon_path=None):
        self.name = name
        self.icon_path = icon_path

    def __str__(self):
        return self.name


class Stream:
    def __init__(self, url, streamer, thumb_url, starts_at, updated_at):
        self.url = url
        self.streamer = streamer
        self.thumb_url = thumb_url
        self.starts_at = starts_at
        self.updated_at = updated_at

    def __str__(self):
        return '{} {} {}'.format(self.starts_at.strftime('%Y/%m/%d %H:%M:%S'), self.streamer, self.url)


def parse_holodule(text):
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

                starts_at = datetime.datetime(datetime.datetime.now().year, month, day_of_month, hours, minutes)

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


def main2():
    # htmlを取得
    res = requests.get('https://schedule.hololive.tv/')

    # htmlを保存
    if not os.path.exists('holodule'):
        os.mkdir('holodule')

    now = datetime.datetime.now()
    savename = 'holodule/{}.html'.format(now.strftime('%Y%m%d-%H%M%S'))

    with open(savename, 'w', encoding=res.encoding) as f:
        f.write(res.text)

    print(f'write {savename}', file=sys.stderr)

    # htmlを解析
    streams = parse_holodule(res.text)

    for stream in streams:
        print(stream)

    streamers = []
    for stream in streams:
        streamers.append(stream.streamer)

    streamers = sorted(set(streamers))  # XXX ハッシュ化不可能なのでエラーが出るはず

    # 永続化
    conn = sqlite3.connect('holodule.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS streams(
                    url          TEXT PRIMARY KEY,
                    streamer_id  INTEGER NOT NULL,
                    starts_at    TEXT,
                    updated_at   TEXT
            )''')
    c.execute('''CREATE TABLE IF NOT EXISTS streamers(
                    name       TEXT PRIMARY KEY,
                    icon_path  TEXT
            )''')

    # streamerを登録
    for streamer in streamers:
        c.execute('''INSERT OR REPLACE INTO streamers VALUES(
                {}, {}
                )'''.format(streamer.name, streamer.icon_path))

    # streamer_idを取得
    c.execute('SELECT name,rowid FROM streamers;')
    rows = c.fetchall()
    streamer_id_by_name = {name: id for name, rowid in rows}

    # streamを登録
    for stream in streams:
        streamer_id = streamer_id_by_name[stream.streamer_name]
        c.execute('''INSERT OR REPLACE INTO streams VALUES(
                {}, {}, {}, {}
                )'''.format(stream.url, streamer_id, stream.starts_at, stream.updated_at))

    conn.commit()
    conn.close()

    return 0


if __name__ == '__main__':
    status = main2()
    if status != 0:
        sys.exit(status)
