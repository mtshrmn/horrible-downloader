# Horrible Downloader    [![Build Status](https://travis-ci.com/mtshrmn/horrible-downloader.svg?branch=master)](https://travis-ci.com/mtshrmn/horrible-downloader) [![codecov](https://codecov.io/gh/mtshrmn/horrible-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/mtshrmn/horrible-downloader)  [![PyPI version](https://badge.fury.io/py/horrible-downloader.svg)](https://badge.fury.io/py/horrible-downloader)

![horrible subs banner](https://i.imgur.com/jWulipo.png)



*Horrible Downloader* is a Python wrapper around the [HorribleSubs](https://horriblesubs.info/) API. It comes with a powerful set of extra features, which allow users to automatically download new episodes and batches of existing shows. The module tracks the downloaded files and allows you to continue from where you left.

## Installation

```sh
> pip install horrible-downloader
```

## Dependencies
**_horrible-downloader_** uses [WebTorrent-CLI](https://github.com/webtorrent/webtorrent-cli) to download its magnets.
The dependency is automatically downloaded with the installation script, but for those who want to install it manualy - simply run ```npm install webtorrent-cli -g```.

**NOTE:** _WebTorrent_ is a NodeJS application, which means you must have Node installed.

## Documentation

#### Usage
example usage of the API inside of Python:
```python
from HorribleDownloader import Parser, ConfigManager

p = Parser()
config = ConfigManager()

download = []
for show, last_watched in config.subscriptions:
    episodes = p.get_episodes(show)
    new = filter(lambda s: s["episode"] > last_watched, episodes)
    download.extend(new)

```

### Using the Parser
for us to do simple interactions with the API we must first initiate a parser object using the `HorribleDownloader.Parser()`.

The parser will allow us to fetch data from [horriblesubs](horriblesubs.info). here are the methods and properties:

- **shows** - List all available shows. equivalent to https://horriblesubs.info/shows/.
- **current_shows** - List all currently airing shows. equivalent to https://horriblesubs.info/current-season/.
- **get_proper_title(title: str, min_threshold=0)** - Returns the exact title using fuzzy string matching.
- **get_episodes(show: str, limit=1000, batches=False)** - Returns a list of episodes from the specified show. By default will return the last 1000 episodes (of course, most shows don't even reach the 100th episode). If `batches` is set to true, it'll simply run as `get_batches` with the same arguments. The function works in reverse, this means the _limit_ argument goes from the latest episode until it reaches its limit (or it has reached the first episode). E.g:
``` python
parser = Parser()
episodes = parser.get_episodes("one piece", limit=7)
# lets assume the latest episode is 495
map(lambda episode: episode["episode"], episodes) # -> [495, 494, 493, 492, 491, 490, 489]

```
- **get_batches(show: str)** - Returns the batches of the show (if it exists).

#### Episode Object

When referring to an episode, the actual representation of it is an object of the following structure:
```python
{
  "title": "the title of the show",
  "episode": "episode number", # represented with a float.
  "480": { # all of the files are in 480p resolution
    "Magnet" "link to magnet",
    "Torrent": "link to the .torrent file",
    "XDCC": "XDCC query", # https://xdcc.horriblesubs.info/
    "Uploaded.net": "uploaded.net link to .mkv",
    "FileUpload": "fileupload link to .mkv",
    "Uplod": "uplod link to .mkv"
  },
  "720": { # exactly the same as the 480, but with 720p resolution
    "Magnet" "link to magnet",
    "Torrent": "link to the .torrent file",
    "XDCC": "XDCC query",
    "Uploaded.net": "uploaded.net link to .mkv",
    "FileUpload": "fileupload link to .mkv",
    "Uplod": "uplod link to .mkv"
  },
  "1080": { # 1080p resolution
    "Magnet" "link to magnet",
    "Torrent": "link to the .torrent file",
    "XDCC": "XDCC query",
    "Uploaded.net": "uploaded.net link to .mkv",
    "FileUpload": "fileupload link to .mkv",
    "Uplod": "uplod link to .mkv"
  }
}
```

---

## Horrible-Subs CLI
A powerful tool for managing and downloading anime in an automatic manner. To run it, simply call `horrible-downloader`.
The CLI is simple, yet effective. It allows you to download the current airing anime, based on your specified subscriptions ([see Configuration](#configuration)), and downloading all the episodes of a desired anime.

#### Featurs:
* use **_horriblesubs_** from the command line.
* minimal configuration
* supports download resuming -- continue exactly where you left!
* allows for smart episode specification parsing.

#### Flags & Options:
The CLI supports manual download of different anime with various options.
Full list of flags and options:
```
$ horrible-downloader --help
usage: horrible-downloader [-h] [-d DOWNLOAD] [-o OUTPUT] [-e EPISODES] [-l]
                           [-r RESOLUTION] [---subscribe SUBSCRIBE] [--batch]
                           [-q] [-lc] [-c CONFIG] [--noconfirm]

horrible script for downloading anime

optional arguments:
  -h, --help                                 show this help message and exit
  -l, --list                                 display list of available shows
  -q, --quiet                                set quiet mode on
  -d DOWNLOAD, --download DOWNLOAD           download a specific anime
  -o OUTPUT, --output OUTPUT                 directory to which it will download the files
  -e EPISODES, --episodes EPISODES           manually specify episodes to download
  -r RESOLUTION, --resolution RESOLUTION     specify resolution quality, defaults to config file
  --subscribe SHOW [-e EPISODE]              add a show to the config file.
  --batch                                    search for batches as well as regular files
  -c CONFIG, --config CONFIG                 config file location
  --noconfirm                                bypass any and all “Are you sure?” messages.
```
##### Episodes & Resolution Formating:
Those two flags have a special syntax which allows for a better specification interface.

###### When using **_episodes_** flag, you can use the following:

|character|usage|example|
|---------|-----|-----|
|,| allows to specify more than one episode or option.|1,6|
|-| specify a range of episodes, including start and end.| 4-10|
|>| bigger than, must be last in order.| 7>|
|<| smaller than, must be first in order.| <10|
|=|equals, in conjunction with < or >, includes the episode number.| 11>=|

###### The **_resolution_** flag syntax is simple, just set the resoultions with the comma (,) between.

`$  horrible-downloader -r 720,1080`

##### Example usage:
The command for downloading episodes 1,2,4,5,6 of "One-Punch Man" to the `~/Videos/Anime` folder:
```bash
$ horrible-downloader -d "one punch man" -e 1,2,4-6 -o ~/Videos/Anime
```
#### Configuration
Once the script is called, the configuration file will be generated in the user's config directory:
`~/.config/horrible-downloader/conf.ini`.
By default, the config file contains all of the current airing anime commented out. To subscribe to an anime, simply uncomment it and specify which episode you're currently on.

**NOTE:** The order of the shows in the config file will affect the order of downloading.

##### example config file:
```
[settings]
resolution = 1080
download_dir = ~/Videos/Anime

[subscriptions]
one punch man = 11
lupin iii part v = 8
jojo's bizzare adventure - golden wind = 0
```

#### Known Issues:
When you use Ctrl+C to interrupt the fetching phase, it will not quit gracefully and will print the traceback of the error. I have no idea how to redirect it to the log file.
