Horrible Downloader
==============

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
from HorribleDownloader import Parser
hs_parser = Parser(conf_dir=".")

current = hs_parser.get_current_shows()
```

## Configuration
By default, once the `Parser()` is called, the configuration file will be generated.
The default is all of the current airing shows. Simply go to the directory specified (default is in current directory) and change the relevant values.