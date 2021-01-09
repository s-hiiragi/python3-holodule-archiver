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
    tr.hidden { display: none; }
    td { border: 1px solid black; }
    img.icon { border-radius: 50%; width: 60px; border: 2px #ff45d5 solid; }
    </style>
    <body>
    <form onsubmit="return false;">
      <select id="name_to_filter2">
        <option value="">名前を選択</option>
      </select>
      <input type="text" id="name_to_filter" placeholder="name">
      <input type="date" id="date_to_filter" placeholder="date">
      <input type="button" id="clear_date_button" value="日付をクリア">
      <input type="button" id="clear_all_button" value="すべてクリア">
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
    <script>
    const nameSelectBox = document.querySelector('#name_to_filter2');
    const nameToFilter = document.querySelector('#name_to_filter');
    const dateToFilter = document.querySelector('#date_to_filter');
    const clearDateButton = document.querySelector('#clear_date_button');
    const clearAllButton = document.querySelector('#clear_all_button');
    const holoduleTableBody = document.querySelector('#holodule_tbody');

    // 名前選択ボックスに名前を追加
    (function(){
      let names = Array.from(document.querySelectorAll('#holodule_tbody td.name')).map(td => td.textContent.trim());
      const nameSet = new Set();
      names.forEach(name => {
        nameSet.add(name);
      });
      names = [...nameSet];
      names.sort();

      names.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        nameSelectBox.appendChild(option);
      });
    })();

    function filterStreams(options) {
      console.log('filterStreams', options);

      const normalizeName = (name) => name.toLowerCase();

      const trs = Array.from(holoduleTableBody.querySelectorAll('tr'));
      trs.forEach(tr => {
        tr.classList.remove('hidden');
      });

      if ('name' in options && options.name !== '') {
        options.name = normalizeName(options.name);
        trs.forEach(tr => {
          const name = normalizeName(tr.querySelector('td.name').textContent.trim());
          if (!name.includes(options.name)) {
            tr.classList.add('hidden');
          }
        });
      }
      if ('date' in options && !isNaN(options.date.getTime())) {
        trs.forEach(tr => {
          const date = new Date(tr.querySelector('td.starts_at').textContent.trim());
          if (options.date.getYear() !== date.getYear() ||
              options.date.getMonth() !== date.getMonth() ||
              options.date.getDate() !== date.getDate()) {
            tr.classList.add('hidden');
          }
        });
      }
    }

    nameSelectBox.addEventListener('change', (e) => {
      nameToFilter.value = '';
      const name = nameSelectBox.value;
      filterStreams({'name': name});
    }, false);

    nameToFilter.addEventListener('input', (e) => {
      nameSelectBox.value = '';
      const name = nameToFilter.value;
      filterStreams({'name': name});
    }, false);

    dateToFilter.addEventListener('change', (e) => {
      const name = nameSelectBox.value || nameToFilter.value;
      const date = new Date(dateToFilter.value);
      filterStreams({'name': name, 'date': date});
    }, false);

    clearDateButton.addEventListener('click', (e) => {
      const name = nameSelectBox.value || nameToFilter.value;
      dateToFilter.value = '';
      filterStreams({'name': name});
    }, false);

    clearAllButton.addEventListener('click', (e) => {
      nameSelectBox.value = '';
      nameToFilter.value = '';
      dateToFilter.value = '';
      filterStreams({});
    }, false);
    </script>
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
