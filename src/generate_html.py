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
    <link rel="stylesheet" href="holodule.css">
    <script defer src="holodule.js"></script>
    <body>
    <form onsubmit="return false;">
      <select id="name_to_filter2">
        <option value="">名前を選択</option>
      </select>
      <input type="text" id="name_to_filter" placeholder="name">
      <input type="date" id="date_to_filter" placeholder="date">
      <input type="button" id="clear_date_button" value="日付をクリア">
      <input type="button" id="clear_all_button" value="すべてクリア">
      <select id="theme">
        <option value="default">デフォルト</option>
        <option value="dark">ダークテーマ</option>
      </select>
    </form>
    <table>
      <thead>
        <th>URL/THUMBNAIL</th>
        <th>NAME</th>
        <th>ICON</th>
        <th>STARTS_AT</th>
      </thead>
      <tbody id="holodule_tbody">
    ''')

    for row in rows:
        starts_at = datetime.datetime.fromisoformat(row[3]).strftime('%Y/%m/%d %H:%M')
        html += dedent('''

            <tr>
              <td class="thumbnail"><a href="{}" target="_blank"><img src="{}" width="160"></a></td>
              <td class="name">{}</td>
              <td class="icon"><img src="{}" class="icon"></td>
              <td class="starts_at">{}</td>
            </tr>
        '''.format(row[0], row[1], row[2], row[4], starts_at))

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
