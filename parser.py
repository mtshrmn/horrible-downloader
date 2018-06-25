def parse_conf(dir: str, file: str):
    import os
    from configparser import ConfigParser

    conf = ConfigParser()
    success = conf.read(os.path.join(dir, file))
    if not success:
        print('No config file found, Generating from default')

        conf['settings'] = {
            'resolution': '1080',
            'download_dir': '~/Videos'
        }

        conf['subscriptions'] = {
            'boku no hero academia': 0,
            'darling in the franxx': 0,
            'steins gate 0': 0,
            'megalo box': 0
        }

        with open(os.path.join(dir, file), 'w') as f:
            conf.write(f)

    return conf


def get_current_shows():
    import sys
    from bs4 import BeautifulSoup
    import requests

    url = 'http://horriblesubs.info/current-season/'

    try:
        html = requests.get(url).text
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    soup = BeautifulSoup(html, 'lxml')
    attributes = {'class': 'ind-show linkful'}
    for anime in soup.find_all(name='div', attrs=attributes):
        yield anime.a.string.lower()


def get_episodes(anime: str):
    import re
    import requests
    from bs4 import BeautifulSoup
    url = "http://horriblesubs.info/lib/search.php?value=" + \
        anime.replace(' ', '-')
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    matches = soup.find_all(name='a', attrs={'title': 'Magnet Link'})
    # check if the this are all of the episodes.
    first_episode_in_batch = None
    for item in matches:
        try:
            first_match_name = matches[0].parent.parent.parent.text.replace('MagnetTorrentULFUUP', '').lower()
            first_episode_in_batch = re.search(r'- (\d+) \[', first_match_name.lower()).group(1)
        except AttributeError:
            matches = matches[1:]

    if first_episode_in_batch:
        for id in range(1, int(int(first_episode_in_batch) / 20) + 1):
            url = "http://horriblesubs.info/lib/search.php?value=" + \
                anime.replace(' ', '-') + '&nextid=' + str(id)
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'lxml')
            matches += soup.find_all(name='a', attrs={'title': 'Magnet Link'})

    for match in matches:
        element = match.parent.parent.parent
        title = element.text.replace('MagnetTorrentULFUUP', '')
        try:
            yield {
                'full name': title,
                'name': anime,
                'episode': re.search(r'- (\d+) \[', title.lower()).group(1),
                'magnet': match['href']
            }
        except AttributeError:
            pass
