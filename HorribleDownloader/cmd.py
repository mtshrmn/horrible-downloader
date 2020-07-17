#!/usr/bin/env python
import os
import sys
import argparse
import logging
from subprocess import call
from typing import List
from multiprocessing import Manager, Lock, Process
from sty import fg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HorribleDownloader import Parser, ConfigManager

try:
    # POSIX system: Create and return a getch that manipulates the tty
    import termios
    import sys
    import tty

    # immitate Windows' msvcrt.getch
    def getch():
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        tty.setraw(file_descriptor)
        ch = sys.stdin.read(1)
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
        return ch

    # Read arrow keys correctly
    def get_key():
        first_char = getch()
        if first_char == '\x1b':
            return {"[A": "up", "[B": "down"}[getch() + getch()]
        return first_char

except ImportError:
    # Non-POSIX: Return msvcrt's (Windows') getch
    from msvcrt import getch

    # Read arrow keys correctly
    def get_key():
        first_char = getch()
        if first_char == b'\xe0':
            return {"H": "up", "P": "down"}[getch().decode("UTF-8")]
        return first_char.decode("UTF-8")

if os.name == "nt":
    # windows
    def clear():
        os.system("cls")
else:
    # linux or osx
    def clear():
        os.system("clear")


def valid_qualities(qualities: List[str]) -> bool:
    for quality in qualities:
        if quality not in ["480", "720", "1080"]:
            return False
    return True


def episode_filter(episode: str, ep_filter: str) -> bool:
    # in charge of parsing the episode flag
    # to better understand this, read the documentation
    for token in ep_filter.split(","):
        # if it's a float (N)
        if token.replace('.', '', 1).isdigit():
            if float(token) == episode:
                return True
        # if it's a range (N1-N2)
        elif "-" in token:
            lower, higher = token.split("-")
            if float(lower) <= episode <= float(higher):
                return True
        # if it's smaller or equal to (=<N)
        elif token.startswith("=<"):
            if episode <= float(token.lstrip("=<")):
                return True
        # if it's smaller than (<N)
        elif token.startswith("<"):
            if episode < float(token.lstrip("<")):
                return True
        # if it's bigger or equal to (N>=)
        elif token.endswith(">="):
            if episode >= float(token.rstrip(">=")):
                return True
        # if it's bigger than (N>)
        elif token.endswith(">"):
            if episode > float(token.rstrip(">")):
                return True
    # if none passes the test, return False
    return False


def download(episode, qualities, path):
    subdir = os.path.join(os.path.expanduser(path), episode["title"].title())
    for quality in qualities:
        call(f"webtorrent \"{episode[quality]['Magnet']}\" -o \"{subdir}\"",
             shell=True)


def fetch_episodes(show_entry, shared_dict, lock, parser, batches, quiet):
    show_title, last_watched = show_entry
    proper_show_title = parser.get_proper_title(show_title)
    if batches:
        batches = parser.get_batches(show_title)
        shared_dict[proper_show_title] = batches[0]
    else:
        episodes = parser.get_episodes(show_title)
        def should_download(episode):
            return float(episode["episode"]) > float(last_watched)
        filtered_episodes = list(filter(should_download, episodes))
        shared_dict[proper_show_title] = filtered_episodes
    if not quiet:
        with lock:
            clear()
            shows = shared_dict.items()
            for title, episodes in shows:
                dots = "." * (50 - len(title))
                if episodes:
                    found_str = f"FOUND ({len(episodes)})"
                    print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(10)}{found_str}{fg.rs}")
                elif episodes == []:
                    print(f"{fg(3)}FETCHING:{fg.rs} {title}{dots} {fg(8)}NONE{fg.rs}")
                else:
                    print(f"{fg(3)}FETCHING:{fg.rs} {title}")

logging.basicConfig(
    level=logging.INFO,
    filename="horribledownloader.log",
    filemode="w",
    format="[%(levelname)s]: %(message)s"
)

def main():
    argparser = argparse.ArgumentParser(description="horrible script for downloading anime")
    argparser.add_argument("-d", "--download", help="download a specific anime", type=str)
    argparser.add_argument("-o", "--output", help="directory to which it will download the files", type=str)
    argparser.add_argument("-e", "--episodes", help="specify specific episodes to download", type=str)
    argparser.add_argument("-l", "--list", help="display list of available episodes", action="store_true")
    argparser.add_argument("-r", "--resolution", help="specify resolution quality", type=str)
    argparser.add_argument("--subscribe", help="add a show to the config file", type=str)
    argparser.add_argument("--batch", help="search for batches as well as regular files", action="store_true")
    argparser.add_argument("-q", "--quiet", help="set quiet mode on", action="store_true")
    argparser.add_argument("-lc", "--list-current", help="list all currently airing shows", action="store_true")
    argparser.add_argument("-c", "--config", help="config file location", type=str)
    argparser.add_argument("--noconfirm", help="Bypass any and all “Are you sure?” messages.", action="store_true")
    args = argparser.parse_args()

    logger = logging.getLogger("info")

    if not args.config:
        config = ConfigManager()
    else:
        path, file = os.path.split(args.config)
        if file:
            config = ConfigManager(conf_dir=path, file=file)
        elif path:
            config = ConfigManager(conf_dir=path)
        else:
            config = ConfigManager()
    parser = Parser()

    if args.subscribe:
        episode_number = args.episodes if args.episodes else "0"
        title = parser.get_proper_title(args.subscribe)
        success, show = config.add_entry(title, episode_number)
        if success:
            print(f"Successfully subscribed to: \"{show.lower()}\"")
            print(f"Latest watched episode is - {episode_number}")
        else:
            print(f"You're already subscribed to \"{show}\", omitting changes...")
        exit(0)

    if args.list:
        print("\n".join(parser.shows.keys()))
        exit(0)

    if args.list_current:
        print("\n".join(parser.current_shows.keys()))
        exit(0)

    clear()

    if args.output:
        config.download_dir = args.output

    if args.resolution:
        config.quality = args.resolution

    qualities = config.quality.split(",")
    if not valid_qualities(qualities):
        print("Bad resolution specified, aborting...")
        exit(1)

    if args.download:
        title = parser.get_proper_title(args.download)
        if not args.quiet:
            print(f"{fg(3)}FETCHING:{fg.rs} {title}")
        episodes = parser.get_episodes(args.download, batches=args.batch)
        def should_download(episode):
            if not args.episodes:
                return True
            return episode_filter(float(episode["episode"]), args.episodes)

        filtered_episodes = list(filter(should_download, episodes))[::-1]
        if not args.quiet:
            clear()
            dots = "." * (50 - len(title))
            found_str = f"FOUND ({len(filtered_episodes)})"
            print(f"{fg(3)}FETCHING: {fg.rs}{title}{dots}{fg(10)}{found_str}{fg.rs}")

            episodes_len = len(filtered_episodes) * len(qualities)
            print(f'{fg(2)}\nFound {episodes_len} file{"s" if episodes_len > 1 else ""} to download:\n{fg.rs}')
            for episode in filtered_episodes:
                for quality in qualities:
                    print(f'{title} - {episode["episode"]} [{quality}p].mkv')

            if not args.noconfirm and not args.quiet:
                inp = input(f'{fg(3)}\nwould you like to proceed? [Y/n] {fg.rs}')
                if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
                    print(fg(1) + 'aborting download\n' + fg.rs)
                    exit(1)

        for episode in filtered_episodes:
            download(episode, qualities, config.download_dir)
        exit(0)


    manager = Manager()
    initial_downloads_dict = {parser.get_proper_title(title): None for title in config.subscriptions.keys()}
    downloads = manager.dict(initial_downloads_dict)
    printing_lock = Lock()
    procs = []
    method = "batches" if args.batch else "show"

    if not args.quiet:
        clear()
        for title in initial_downloads_dict.keys():
            print(f"{fg(3)}FETCHING:{fg.rs} {title}")

    for entry in config.subscriptions.items():
        proc = Process(
            target=fetch_episodes,
            args=(entry, downloads, printing_lock, parser, args.batch, args.quiet)
        )
        proc.start()
        procs.append(proc)

    for proc in procs:
        proc.join()

    downloads_list = []
    for episodes in downloads.values():
        downloads_list.extend(reversed(episodes))

    if downloads_list == []:
        if not args.quiet:
            print(fg(1) + 'No new episodes were found. Exiting ' + fg.rs)
        logger.info("No new episodes were found. Exiting ")
        exit(0)

    logger.info("found the following files:")
    if not args.quiet:
        episodes_len = len(downloads_list) * len(qualities)
        print(f'{fg(2)}\nFound {episodes_len} file{"s" if episodes_len > 1 else ""} to download:\n{fg.rs}')
    for episode in downloads_list:
        for quality in qualities:
            if not args.quiet:
                print(f'{episode["title"]} - {episode["episode"]} [{quality}p].mkv')
            logger.info(f'{episode["title"]} - {episode["episode"]} [{quality}p].mkv')

    if not args.noconfirm and not args.quiet:
        inp = input(f'{fg(3)}\nwould you like to proceed? [Y/n] {fg.rs}')
        if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
            print(fg(1) + 'aborting download\n' + fg.rs)
            logger.info("user has aboorted the download")
            exit(1)


    for episode in downloads_list:
        download(episode, qualities, config.download_dir)
        config.update_entry(episode["title"], episode["episode"])
        logger.info(f'updated entry: {episode["title"]} - {episode["episode"]}')
    exit(0)

if __name__ == "__main__":
    main()
