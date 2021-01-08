# Holodule Archiver


## Motivation

[Holodule](https://schedule.hololive.tv) is a wonderful website to grasp a day schedule of hololive production members.
I want to see the past schedule sometimes so I save the webpage into a database by this scripts.
For the present you can create a html that contains all the past schedule by using generate_html.py.


## How to create a develop/runtime environment

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


## License

Apache License 2.0

