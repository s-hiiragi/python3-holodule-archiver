import os
import sys
import datetime
import requests
import argparse
from .setting import holodule_dir


def fetch(outdir):
    # htmlを取得

    holodule_url = 'https://schedule.hololive.tv/'

    print(f'fetching {holodule_url} ...', file=sys.stderr)
    res = requests.get(holodule_url)

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    now = datetime.datetime.now()
    savename = os.path.join(outdir, '{}.html'.format(now.strftime('%Y%m%d-%H%M%S')))
    savename = os.path.abspath(savename)

    with open(savename, 'w', encoding=res.encoding) as f:
        f.write(res.text)

    print(f'write {savename}', file=sys.stderr)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-O', '--outdir')
    args = argparser.parse_args()

    outdir = args.outdir or holodule_dir

    fetch(outdir)


if __name__ == '__main__':
    main()
