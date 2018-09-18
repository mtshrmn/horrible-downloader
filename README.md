Horrible Downloader
==============

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4a13ba5715f94427998e63968ea710d7)](https://app.codacy.com/app/Jelomite/horrible-downloader?utm_source=github.com&utm_medium=referral&utm_content=Jelomite/horrible-downloader&utm_campaign=Badge_Grade_Settings)

![horrible subs banner](http://horriblesubs.info/images/b/ccs_banner.jpg)

A ~~small~~ horrible command line tool meant for downloading ongoing horrible anime.

This script rips the magnet link out of HorribleSubs' RRS feed downloads it using the webtorrent-cli.

Plus it also makes a `history` file for keeping track of which magnets have been downloaded already.

## Installation
```sh
$ git clone https://github.com/jelomite/horrible-downloader.git
$ cd horrible-downloader
$ pip install .
$ pip install -r requirements.txt
```

## Usage
example usage of the API
```python
from HorribleDownloader import Parser, ConfigManager

p = Parser()
config = ConfigManager()

download = []
for show, last_watched in config.subscriptions:
    episodes = p.get_episodes(show)
    new = filter(lambda s: float(s["episode"]) > float(last_watched), episodes)
    download.extend(new)
    
```

## Configuration
By default, once the `Parser()` is called, the configuration file will be generated.
The default is all of the current airing shows. Simply go to the directory specified (default is in current directory) and change the relevant values.