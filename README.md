# Horrible Downloader    [![Codacy Badge](https://api.codacy.com/project/badge/Grade/4a13ba5715f94427998e63968ea710d7)](https://app.codacy.com/app/Jelomite/horrible-downloader?utm_source=github.com&utm_medium=referral&utm_content=Jelomite/horrible-downloader&utm_campaign=Badge_Grade_Settings)

![horrible subs banner](http://horriblesubs.info/images/b/ccs_banner.jpg)



*Horrible Downloader* is a Python wrapper around the [HorribleSubs](https://horriblesubs.info/) API. It comes with a powerful set of extra features, which allow users to automatically download new episodes and batches of existing shows. The module tracks the downloaded files and allows you to continue from where you left. 

## Installation
```sh
$ git clone https://github.com/jelomite/horrible-downloader.git
$ cd horrible-downloader
$ pip install .
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
    new = filter(lambda s: s["episode"] > last_watched, episodes)
    download.extend(new)
    
```

## Horrible-Subs CLI
A powerful tool for managing and downloading anime in an automatic manner. To run it, simply call `horrible-downloader`.
The CLI is simple, yet effective. It allows you to download the current airing anime, based on your specified subscriptions ([see Configuration](#configuration)), and downloading all the episodes of a desired anime. 

## Configuration
Once the script is called, the configuration file will be generated in the user's config directory:
`~/.config/horrible-downloader/conf.ini`.
By default, the config file contains all of the current airing anime commented out. To subscribe to an anime, simply uncomment it and specify which episode you're currently on.
