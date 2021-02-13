import os
import sys
import sqlite3
import datetime
from jinja2 import Template
from textwrap import dedent
from .setting import dbname


def generate_render_data():
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

    return {
        'streams': streams
    }


def generate_html():
    with open('templates/holodule.html', encoding='UTF-8') as f:
        template_html = f.read()

    render_data = generate_render_data()

    template = Template(template_html)
    html = template.render(render_data)

    savename = 'holodule.html'
    savename = os.path.abspath(savename)

    with open(savename, 'w', encoding='UTF-8') as f:
        f.write(html)

    print(f'write {savename}', file=sys.stderr)


def main():
    generate_html()


if __name__ == '__main__':
    main()
