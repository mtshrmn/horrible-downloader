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
```

## Usage
just run the script
```sh
$ python horrible-downloader.py
```

## Configuration
for the default configuration, which includes all of the current season shows, you can simply enter the following command:
```sh
$ python horrible-downloader.py --generate-config
```
once generated, you will see the config file in the same directory as the script. you can modify it as you wish.


## Requirements
* [feedparser](https://pypi.python.org/pypi/feedparser)
* [webtorrent-cli](https://github.com/webtorrent/webtorrent-cli)
