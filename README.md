# Horrible Downloader    [![Codacy Badge](https://api.codacy.com/project/badge/Grade/4a13ba5715f94427998e63968ea710d7)](https://app.codacy.com/app/Jelomite/horrible-downloader?utm_source=github.com&utm_medium=referral&utm_content=Jelomite/horrible-downloader&utm_campaign=Badge_Grade_Settings)

![horrible subs banner](http://horriblesubs.info/images/b/ccs_banner.jpg)



*Horrible Downloader* is a Python wrapper around the [HorribleSubs](https://horriblesubs.info/) API. It comes with a powerful set of extra features, which allow users to automatically download new episodes and batches of existing shows. The module tracks the downloaded files and allows you to continue from where you left. 

## Installation
```sh
$ git clone https://github.com/jelomite/horrible-downloader.git
$ cd horrible-downloader
$ pip install .
```

## Dependencies
**_horrible-downloader_** uses [WebTorrent-CLI](https://github.com/webtorrent/webtorrent-cli) to download its magnets. 
The dependency is automatically downloaded with the installation script, but for those who want to install it manualy - simply run ```npm install webtorrent-cli -g```.

**NOTE:** _WebTorrent_ is a NodeJS application, which means you must have Node installed. 

## Usage
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

## Horrible-Subs CLI
A powerful tool for managing and downloading anime in an automatic manner. To run it, simply call `horrible-downloader`.
The CLI is simple, yet effective. It allows you to download the current airing anime, based on your specified subscriptions ([see Configuration](#configuration)), and downloading all the episodes of a desired anime. 

#### Featurs:
* use **_horriblesubs_** from the command line.
* minimal configuration
* supports download resuming -- continue exactly where you left!
* allows for smart episode specification parsing.

#### Example usage:
```bash
$ horrible-downloader -d "one punch man" -e 1,2,4-6 -o ~/Videos/Anime
```
#### Configuration
Once the script is called, the configuration file will be generated in the user's config directory:
`~/.config/horrible-downloader/conf.ini`.
By default, the config file contains all of the current airing anime commented out. To subscribe to an anime, simply uncomment it and specify which episode you're currently on.

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
