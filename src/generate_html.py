import sqlite3
import datetime
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

    html = dedent('''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta charset="UTF-8">
    <style>
    td { border: 1px solid black; }
    img.icon { border-radius: 50%; width: 60px; border: 2px #ff45d5 solid; }
    </style>
    <body>
    <table>
      <thead>
        <th>URL/THUMBNAIL</th>
        <th>NAME</th>
        <th>STARTS_AT</th>
        <th>ICON</th>
      </thead>
      <tbody>
    ''')

    for row in rows:
        starts_at = datetime.datetime.fromisoformat(row[3]).strftime('%Y/%m/%d %H:%M')
        html += dedent('''
          <tr>
            <td><a href="{}" target="_blank"><img src="{}" width="160"></a></td>
            <td>{}</td>
            <td>{}</td>
            <td><img src="{}" class="icon"></td>
          </tr>
        '''.format(row[0], row[1], row[2], starts_at, row[4]))

    html += dedent('''
      </tbody>
    </table>
    </body>
    </html>
    ''')

    with open('holodule.html', 'w', encoding='UTF-8') as f:
        f.write(html)

    conn.close()


def main():
    generate_html()


if __name__ == '__main__':
    main()
