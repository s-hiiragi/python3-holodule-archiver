import sqlite3
import datetime
from jinja2 import Template
from textwrap import dedent
from .setting import dbname


def generate_html():
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('''
            SELECT url, thumb_url, streamer_name, starts_at, icon_path
              FROM streams
              INNER JOIN streamers
              ON streams.streamer_name = streamers.name
              ORDER BY starts_at ASC''')
    rows = cur.fetchall()
    conn.close()

    streams = []
    for row in rows:
        starts_at = datetime.datetime.fromisoformat(row[3]).strftime('%Y/%m/%d %H:%M')
        streams.append({
            'url': row[0],
            'thumb_url': row[1],
            'streamer_name': row[2],
            'icon_url': row[4],
            'starts_at': starts_at
        })

    with open('templates/holodule.html', encoding='UTF-8') as f:
        template_html = f.read()

    template = Template(template_html)
    html = template.render({'streams': streams})

    with open('holodule.html', 'w', encoding='UTF-8') as f:
        f.write(html)


def main():
    generate_html()


if __name__ == '__main__':
    main()
