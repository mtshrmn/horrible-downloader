import re
import os
import sys
import subprocess
import feedparser
from bs4 import BeautifulSoup
import argparse
import requests

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
        print(
            f'"{anime}" isnt in the current season shows, please check for correctness')
        sys.exit(1)

anime_feed = feedparser.parse("http://horriblesubs.info/rss.php?res=all")

links = []
quality = parsed_config['quality']
for anime in parsed_config['anime']:
    r = re.compile(
        r'\[HorribleSubs\] {} - \d+ \[{}p\]\.mkv'.format(anime, quality), flags=re.IGNORECASE)
    for entry in anime_feed.entries:
        if r.match(str(entry.title)):
            links.append({
                'title': entry.title,
                'date': entry.published_parsed,
                'magnet': entry.link
            })
subprocess.call(['clear'])
print('found new episodes to download: \n')
for link in links:
    print(link['title'])

inp = input('\nwould you like to proceed? [Y/n] ')
if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
    print('aborting download')
    sys.exit(1)

path = os.path.expanduser(parsed_config['path'])

for link in links:
    subprocess.call(['webtorrent', link['magnet'], '-o', path])

sys.exit(0)
