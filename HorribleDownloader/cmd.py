#!/usr/bin/env python

import os
import argparse
import subprocess
from HorribleDownloader import Parser, ConfigManager
from sty import fg
import multiprocessing
from functools import partial

def clear(): # function to clear the screan
    os.system("cls" if os.name == "nt" else "clear")

def subscribe_to(show, episode):
    """
    subscribe to a show at and set progress to specified episodes
    :param show: the search term for the name of the show, it can be an approximation
    :param episode: the initial episode to set the show. defaults to 0 (as if no episodes were watched).
    :return: returns a tuple - first element indicates the success status, the second one is the exact name of the show.
    """
    config = ConfigManager()
    title = Parser().get_episodes(show)[0]["title"]

    if title.lower() in config.conf["subscriptions"]:
        return False, title

    config.conf["subscriptions"][title.lower()] = episode
    with open(os.path.join(config.dir, config.file), "w") as f:
        config.conf.write(f)

    return True, title

def verify_quality(qualities):
    """
    checks if quality is in a valid format (480, 720, 1080).
    :param qualities: array of qualities
    :return: true if format is right.
    """
    for quality in qualities:
        if quality not in ["480", "720", "1080"]:
            return False
    return True

def generate_episode_filter(episodes):
    """
    parse the episode specification string to generate a filter function.
    read the docs for understanding the syntax.
    :param episodes: the episode specification string
    :return: filter function for the episodes
    """
    # if no episodes where specified - the generated filter should return false.
    if not episodes:
        def default_filter():
            return False
        return default_filter

    tests = []
    for token in episodes.split(","):
        # we have multiple options:
        # N, N1-N2, =<N, <N, N>=, N>
        # each of those options adds a test to a list.
        # if one tests passes -> we keep the episode.
        if token.replace('.', '', 1).isdigit():
            tests.append(partial(lambda t, ep: ep == t, float(token)))

        elif "-" in token:
            numbers = token.split("-")
            tests.append(partial(lambda n1, n2, ep: float(n1) <= ep <= float(n2), *numbers))

        elif token.startswith("=<"):
            tests.append(partial(lambda t, ep: ep <= t, float(token.lstrip("=<"))))

        elif token.startswith("<"):
            tests.append(partial(lambda t, ep: ep < t, float(token.lstrip("<"))))

        elif token.endswith(">="):
            tests.append(partial(lambda t, ep: ep >= t, float(token.rstrip(">="))))

        elif token.endswith(">"):
            tests.append(partial(lambda t, ep: ep > t, float(token.rstrip(">"))))

        else:
            raise RuntimeError("invalid query")

    def generated_filter(ep):
        return any([test(float(ep)) for test in tests])

    return generated_filter

def download(episode, qualities, path):
    """
    the actual download function
    :param episode: episode object
    :param qualities: the specified qualities
    :param download_dir: absolute path to the directory for downloading the files
    """
    subdir = os.path.join(path, episode["title"].title())
    for quality in qualities:
        subprocess.call(f"webtorrent \"{episode[quality]['Magnet']}\" -o \"{subdir}\"", shell=True)

def fetch_episodes(parser, show, last_watched, shared_data, global_args):
    # default values for
    new = []
    shared_data[show] = []
    # print info if not quiet mode
    if not global_args.quiet:
        titles = shared_data.keys()
        clear()
        for title in titles:
            print(f"{fg(3)}FETCHING:{fg.rs} {title}")

    if global_args.batch:
        new = parser.get_batches(show)
        shared_data[show] = new[0]
    else:
        episodes = parser.get_episodes(show)
        if global_args.episodes:
            ep_filter = generate_episode_filter(global_args.episodes)
            new = list(filter(lambda s: ep_filter(s["episode"]), episodes))
        else:
            new = list(filter(lambda s: float(s["episode"]) > float(last_watched), episodes))

        shared_data[show] = new if new else None

    # print the dots...
    if not global_args.quiet:

        titles = shared_data.keys()
        clear()
        for title in titles:
            dots = "." * (50 - len(str(title)))
            if shared_data[title]:
                print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(10)}FOUND ({str(len(shared_data[title]))}){fg.rs}")
            else:
                if shared_data[title] is None:
                    print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(8)}NONE{fg.rs}")
                else:
                    print(f"{fg(3)}FETCHING:{fg.rs} {title}")

def flatten_dict(dictionary):
    # flatten a dictionary into a list.
    # the transformation:
    # {"key1": [val1, val2, ...], "key2": [val3, val4, ...], ...} -> [val1, val2, val3, val4, ...]
    flat = []
    for key in dictionary.keys():
        if dictionary[key]:
            flat.extend(dictionary[key])

    return flat

def reprint_results(data, qualities):
    # resets console output until the state of re-arranging
    titles = data.keys()
    clear()
    for title in titles:
        dots = "." * (50 - len(str(title)))
        if data[title]:
            print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(10)}FOUND ({str(len(data[title]))}){fg.rs}")
        else:
            print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(8)}NONE{fg.rs}")

    data_flat = flatten_dict(data)
    print(f'{fg(2)}\nFound {len(data_flat)} {"files" if len(data_flat) > 1 else "file"} to download:\n{fg.rs}')
    for episode in data_flat:
        for quality in qualities:
            print(f'{episode["title"]} - {episode["episode"]} [{quality}p].mkv')

def main(args):
    clear()
    CONFIG = ConfigManager()
    PARSER = Parser()
    # change to custom download dir if user has specified
    if args.output:
        CONFIG.download_dir = args.output

    QUALITIES = (CONFIG.quality if not args.resolution else args.resolution).split(",")
    # validating qualities object to fit format:
    if not verify_quality(QUALITIES):
        print("Bad resolution specified, aborting...")
        exit(1)

    downloads = []
    if args.download: # we want to set the correct title
        title = Parser().get_episodes(args.download)[0]["title"]

    downloads = multiprocessing.Manager().dict()
    procs = []

    # all the variables set, lets start with the iterations:
    for show, last_watched in [(title, 0)] if args.download else CONFIG.subscriptions:
        proc = multiprocessing.Process(
        target=fetch_episodes,
        args=(PARSER, show, last_watched, downloads, args))

        proc.start()
        procs.append(proc)

    for proc in procs:
        proc.join()

    downloads_flat = flatten_dict(downloads)

    # after we iterated on all of the shows we have a list of stuff to download.
    # but first we must check the list if it contains data:
    if not downloads_flat:
        if args.download: # we want to display a different message in each case.
            print(fg(1) + "Couldn't find specified anime. Exiting" + fg.rs)
        else:
            print(fg(1) + 'No new episodes were found. Exiting ' + fg.rs)
        exit(1) # arguably should be exit code 0

    # summerizing info about the download
    reprint_results(downloads, QUALITIES)
    inp = input(f'{fg(3)}\nwould you like to re-arrange the downloads? (Return for default) {fg.rs}')
    if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
        print(fg(1) + 'aborting download\n' + fg.rs)
        exit(1)

    #l et the downloads begin!
    abs_path = os.path.expanduser(CONFIG.download_dir)
    for episode_obj in reversed(downloads):
        download(episode_obj, QUALITIES, abs_path)

        if not args.download:
            CONFIG.conf["subscriptions"][episode_obj["title"].lower()] = episode_obj["episode"].lstrip("0")
            with open(os.path.join(CONFIG.dir, CONFIG.file), "w") as f:
                CONFIG.conf.write(f)

def cli():
    parser = argparse.ArgumentParser(description='horrible script for downloading anime')
    parser.add_argument('-d', '--download', help="download a specific anime", type=str)
    parser.add_argument('-o', '--output', help="directory to which it will download the files", type=str)
    parser.add_argument('-e', '--episodes', help="specify specific episodes to download", type=str)
    parser.add_argument('-l', '--list', help="display list of available episodes", action="store_true")
    parser.add_argument('-r', '--resolution', help="specify resolution quality", type=str)
    parser.add_argument('--subscribe', help="add a show to the config file", type=str)
    parser.add_argument('--batch', help="search for batches as well as regular files", action="store_true")
    parser.add_argument('-q', '--quiet', help="set quiet mode on", action="store_true")
    parser.add_argument('-lc', '--list-current', help="list all currently airing shows", action="store_true")
    args = parser.parse_args()

    if args.subscribe:
        episode_number = args.episodes if args.episodes else "0"
        status, show = subscribe_to(args.subscribe, episode_number)

        if status:
            print(f"Successfully subscribed to: \"{show.lower()}\"")
            print(f"Latest watched episode is - {episode_number}")
        else:
            print(f"You're already subscribed to \"{show}\", omitting changes...")
        exit(0)

    if args.list:
        shows = list(Parser().shows.keys())
        print("\n".join(shows))
        exit(0)

    if args.list_current:
        shows = list(Parser().current_shows)
        print("\n".join(shows))
        exit(0)

    main(args)


if __name__ == "__main__":
    cli()
