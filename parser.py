import re
import os
import sys
import subprocess
import feedparser
from bs4 import BeautifulSoup
import requests
import json

subprocess.call(['clear'])

with open('config', mode='r') as f:
    text = iter(f.read().split('\n'))
    parsed_config = {}

    while True:
        try:
            line = next(text)
            if line.startswith('#'):
                continue
            if line == 'resolution:':
                parsed_config['quality'] = next(text).strip(' ')

            if line == 'download_dir:':
                parsed_config['path'] = next(text).strip(' ')

            if line == 'anime:':
                parsed_config['anime'] = []
                while True:
                    show = next(text).strip(' ')
                    if show:
                        parsed_config['anime'].append(show)
        except StopIteration:
            break

with open('watch.json', mode='r') as f:
    last_episode = json.load(f)

for show in parsed_config['anime']:
    if show not in last_episode.keys():
        i = input(f'"{show}" does not appear to be in the history file, would you like to add it? [Y/n]')
        if i not in ('', 'Y', 'y', 'yes', 'Yes'):
            print('please manualy adjust the config file')
            sys.exit(1)

        last_episode[show] = 0

url = 'http://horriblesubs.info/current-season/'
print('fetching feed...')

try:
    html = requests.get(url).text
except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)

soup = BeautifulSoup(html, 'lxml')
current_season = []

for anime in soup.find_all(name='div', attrs={'class': 'ind-show linkful'}):
    current_season.append(anime.a.string.lower())

for anime in parsed_config['anime']:
    if anime not in current_season:
        print(f'"{anime}" is not in the current season shows, please spell check the config file.')
        sys.exit(1)

anime_feed = feedparser.parse("http://horriblesubs.info/rss.php?res=all")

links = []
tmp_links = []
quality = parsed_config['quality']
for anime in parsed_config['anime']:
    r = re.compile(r'\[HorribleSubs\] {} - \d+ \[{}p\]\.mkv'.format(anime, quality), flags=re.IGNORECASE)
    for entry in anime_feed.entries:
        if r.match(str(entry.title)):
            current_episode = entry.title.lower().strip(f'[horriblesubs] {anime} - ').replace(f'[{quality}p].mkv', '')
            links.append({
                'title': entry.title,
                'episode': current_episode,
                'magnet': entry.link
            })
        else:
            current_episode = 1000
            for e in anime_feed.entries:
                if r.match(str(e.title)):
                    current_episode = e.title.lower().strip(f'[horriblesubs] {anime} - ').replace(f'[{quality}p].mkv', '')
        entry_title = entry.title.lower().replace('[horriblesubs] ', '')
        entry_title = entry_title.replace(f'[{quality}p].mkv', '')
        entry_title = ' - '.join(entry_title.split(' - ')[:-1])
        if int(current_episode) > int(last_episode[anime]) and entry_title in parsed_config['anime']:
            search_url = "http://horriblesubs.info/lib/search.php?value=" + anime.replace(' ', '-')
            search_html = requests.get(search_url).text
            tmp_soup = BeautifulSoup(search_html, 'lxml')

            matches = tmp_soup.find_all(name='a', attrs={'title': 'Magnet Link'})

            for match in reversed(matches):
                element = match.parent.parent.parent
                title = element.text.replace('MagnetTorrentULFUUP', '')
                stripped = title.lower().strip(anime + '- ')
                if quality in stripped:
                    episode = stripped.replace(f'[{quality}p]', '')
                    try:
                        if int(last_episode[anime]) < int(episode) < int(current_episode):
                            tmp_links.append({
                                'title': f'[HorribleSubs] {title}.mkv',
                                'episode': episode,
                                'magnet': match['href']
                            })
                    except ValueError:
                        pass
            else:
                last_episode[anime] = episode
links += tmp_links

# subprocess.call(['clear'])
print('found new episodes to download: \n')

for link in sorted(links, key=lambda l: l['title'], reverse=True):
    print(link['title'])

inp = input('\nwould you like to proceed? [Y/n] ')
if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
    print('aborting download')
    sys.exit(1)

with open('watch.json', mode='w') as f:
    json.dump(last_episode, f)

path = os.path.expanduser(parsed_config['path'])

for link in links:
    subprocess.call(['webtorrent', link['magnet'], '-o', path])

sys.exit(0)
