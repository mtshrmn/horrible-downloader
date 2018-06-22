import re
import os
import subprocess
import feedparser
from bs4 import BeautifulSoup
import argparse
import requests
animes = ['alice or alice', 'steins gate 0']
url = 'http://horriblesubs.info/current-season/'
html = requests.get(url).text

soup = BeautifulSoup(html, 'lxml')
items = soup.find_all(name='div', attrs={'class': 'ind-show linkful'})
current_season = []
for item in items:
    current_season.append(item.a.string.lower())
print('fetching feed...')
anime_feed = feedparser.parse("http://horriblesubs.info/rss.php?res=all")

links = []
for anime in animes:
    if anime not in current_season:
        print(f'"{anime}" isnt in the current season shows, please check for correctness')
        break;
    r = re.compile(r'\[HorribleSubs\] {} - \d+ \[1080p\]\.mkv'.format(anime), flags=re.IGNORECASE)
    for entry in anime_feed.entries:
        if r.match(str(entry.title)):
            print(entry.title)
            links.append(entry.link)
path = os.path.join('downloads')
for link in links:
    subprocess.call(['webtorrent', link, '-o', path])
