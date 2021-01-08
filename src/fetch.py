import os
import sys
import datetime
import requests
from .setting import holodule_dir


def fetch():
    # htmlを取得

    res = requests.get('https://schedule.hololive.tv/')

    if not os.path.exists(holodule_dir):
        os.mkdir(holodule_dir)

    now = datetime.datetime.now()
    savename = os.path.join(holodule_dir, '{}.html'.format(now.strftime('%Y%m%d-%H%M%S')))

    with open(savename, 'w', encoding=res.encoding) as f:
        f.write(res.text)

    print(f'write {savename}', file=sys.stderr)


def main():
    fetch()


if __name__ == '__main__':
    main()
