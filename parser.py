import re
import os
import subprocess
import feedparser
from bs4 import BeautifulSoup
import argparse

animes = ['alice or alice', 'steins gate 0']
current_season = []
print('fetching feed...')
anime_feed = feedparser.parse("http://horriblesubs.info/rss.php?res=all")
for anime in animes:
    if anime not in current_season:
        print(f'"{anime}" isnt in the current season shows, please check for correctness')
        break;
    r = re.compile(r'\[HorribleSubs\] {} - \d+ \[1080p\]\.mkv'.format(anime), flags=re.IGNORECASE)
    for entry in anime_feed.entries:
        if r.match(str(entry.title)):
            print(entry.title)
