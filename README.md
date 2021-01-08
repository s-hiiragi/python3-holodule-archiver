# Holodule Archiver


## How to create a develop environment

```py
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```


## Scripts

| Name          | Description                                     | Command                  |
| ------------- | ----------------------------------------------- | ------------------------ |
| fetch         | Fetch a html from https://schedule.hololive.tv/ | python -m src.fetch      |
| parse         | Parse html files and store it into the database | python -m src.parse [-f] |
| generate_html | Generate a html from the database               | python -m generate_html  |

Default locations of html files and a database:
See setting.py
