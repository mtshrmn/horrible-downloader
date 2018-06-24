import os
import sys
from parser import *
from subprocess import call
import argparse


def main(download, custom_dir):
    call(['clear'])

    # set some variables:
    dir = '/'.join(sys.argv[0].split('/')[:-1])
    config = parse_conf(dir, 'conf.ini')
    quality = config['settings']['resolution']
    download_dir = config['settings']['download_dir'] if not custom_dir else custom_dir
    subscriptions = config['subscriptions'] if not download else {download: 0}

    # check integrity of quality
    if quality not in ('480', '720', '1080'):
        print(f'{quality} isn\'t a valid option. please choose from [480|720|1080]')
        sys.exit(1)

    # get the currently airing shows:
    print('fetching feed...')
    if not download:
        airing = list(get_current_shows())
    else:
        airing = []

    to_download = []
    for show in subscriptions:
        # check integrity of subscriptions
        if show not in airing and not download:
            print(f'"{show.title()}" doesn\'t currently air. please fix this in the configuration file')
            sys.exit(1)
        last_episode_watched = int(subscriptions[show])
        episodes = list(get_episodes(show))
        filter_key = lambda e: int(e['episode']) > last_episode_watched and quality in e['full name']
        to_download += [episode for episode in filter(filter_key, episodes)]

    if len(to_download) is 0:
        print('No new episodes were found. Exiting ')
        sys.exit(1)

    call(['clear'])

    print(f'\nFound {len(to_download)} episodes to download:\n')
    for episode in to_download:
        print(f'{episode["full name"]}.mkv')

    inp = input('\nwould you like to proceed? [Y/n] ')
    if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
        print('aborting download\n')
        sys.exit(1)

    # let the downloads begin!
    path = os.path.expanduser(download_dir)
    print(f'Beginning download to {path}')
    for show in reversed(to_download):
        subdir = os.path.join(path, show['name'].title())
        call(['webtorrent', show['magnet'], '-o', subdir])
        if not download:
            config['subscriptions'][show['name']] = show['episode']
            with open(os.path.join(dir, 'conf.ini'), 'w') as f:
                config.write(f)
            call(['clear'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='horribly download anime')
    parser.add_argument('-d', '--download', help="download a specific animer", type=str)

    parser.add_argument('-o', '--output', help="directory to which it will download the files",
                        type=str)

    args = parser.parse_args()
    main(args.download, args.output)
