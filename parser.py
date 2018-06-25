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

    assert conf['settings']['resolution'] in ('480', '720', '1080')
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
    import sys
    import requests
    from bs4 import BeautifulSoup

    repisode = re.compile(r'- (\d+) \[')
    id = 0  # initialization of the nextid in the api call
    matches = []  # the list in which we will append our links

    while True:
        url = "http://horriblesubs.info/lib/search.php?value=" + \
            anime.replace(' ', '-') + '&nextid=' + str(id)
        try:
            html = requests.get(url).text
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        soup = BeautifulSoup(html, 'lxml')
        findings = soup.find_all(name='a', attrs={'title': 'Magnet Link'})
        if not findings:  # if we dont find anything, it means we are done here.
            break
        id += 1
        matches.extend(findings)

    for match in matches:
        element = match.parent.parent.parent
        title = element.text.replace('MagnetTorrentULFUUP', '')
        try:
            yield {
                'full name': title,
                'name': anime,
                'episode': repisode.search(title.lower()).group(1),
                'magnet': match['href']
            }
        except AttributeError:
            pass
