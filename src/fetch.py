import os
import sys
import datetime
import requests
import argparse
import logging
from .setting import holodule_dir


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(module)s: %(message)s'))
logger.addHandler(handler)
logging = None  # do not use logging.info


def fetch(outdir):
    # htmlを取得

    holodule_url = 'https://schedule.hololive.tv/'

    logger.info(f'fetching {holodule_url} ...')
    res = requests.get(holodule_url)

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    now = datetime.datetime.now()
    savename = os.path.join(outdir, '{}.html'.format(now.strftime('%Y%m%d-%H%M%S')))
    savename = os.path.abspath(savename)

    with open(savename, 'w', encoding=res.encoding) as f:
        f.write(res.text)

    logger.info(f'write {savename}')


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-O', '--outdir')
    args = argparser.parse_args()

    outdir = args.outdir or holodule_dir

    fetch(outdir)


if __name__ == '__main__':
    main()
