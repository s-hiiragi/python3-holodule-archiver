# Holodule Archiver


## Motivation

[Holodule](https://schedule.hololive.tv) is a wonderful website to grasp a day schedule of hololive production members.
I want to see the past schedule sometimes so I save the webpage into a database by this scripts.
For the present you can create a html that contains all the past schedule by using generate_html.py.


## Python Scripts

| Name          | Description                                     | Command                     |
| ------------- | ----------------------------------------------- | --------------------------- |
| fetch         | Fetch a html from https://schedule.hololive.tv/ | python -m src.fetch         |
| parse         | Parse html files and store it into the database | python -m src.parse [-f]    |
| generate_html | Generate a html from the database               | python -m src.generate_html |
| server        | Run a web server for development (using Flask)  | python -m src.server        |

Default locations of html files and a database:
See setting.py


## How to create a develop/runtime environment

Windows 10

```console
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Ubuntu 20.04

```console
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## How to edit crontab settings

crontab settings (1/2)

```console
crontab -e
```

```txt
5 0,12 * * * /home/USER/python3-holodule-archiver/scripts/fetch-parse-generate
```

crontab settings (2/2)

```console
sudo crontab -e
```

```console
7 0,12 * * * /home/hii/repo/python3-holodule-archiver/scripts/deploy
```


## License

Apache License 2.0

