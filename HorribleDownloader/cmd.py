#!/usr/bin/env python
import os
import sys
import argparse
import logging
from multiprocessing import Manager, Lock, Process
from sty import fg

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HorribleDownloader import Parser, ConfigManager
from cmd_funcs import (
    valid_qualities,
    episode_filter,
    download,
    clear,
    fetch_episodes)


class StreamToLogger:
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

logging.basicConfig(
    level=logging.INFO,
    filename="horribledownloader.log",
    filemode="w",
    format="[%(levelname)s]: %(message)s"
)

stderr_logger = logging.getLogger('STDERR')
logger = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = logger

if __name__ == "__main__":
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

    clear()

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

        filtered_episodes = list(filter(should_download, episodes))
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
            config.update_entry(title, episode["episode"])
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
        for episode in episodes:
            downloads_list.append(episode)

    if downloads_list == []:
        if not args.quiet:
            print(fg(1) + 'No new episodes were found. Exiting ' + fg.rs)
        logging.info("No new episodes were found. Exiting ")
        exit(0)

    logging.info("found the following files:")
    if not args.quiet:
        episodes_len = len(downloads_list) * len(qualities)
        print(f'{fg(2)}\nFound {episodes_len} file{"s" if episodes_len > 1 else ""} to download:\n{fg.rs}')
    for episode in downloads_list:
        for quality in qualities:
            if not args.quiet:
                print(f'{episode["title"]} - {episode["episode"]} [{quality}p].mkv')
            logging.info(f'{episode["title"]} - {episode["episode"]} [{quality}p].mkv')

    if not args.noconfirm and not args.quiet:
        inp = input(f'{fg(3)}\nwould you like to proceed? [Y/n] {fg.rs}')
        if inp not in ('', 'Y', 'y', 'yes', 'Yes'):
            print(fg(1) + 'aborting download\n' + fg.rs)
            logging.info("user has aboorted the download")
            exit(1)


    for episode in downloads_list:
        download(episode, qualities, config.download_dir)
        config.update_entry(episode["title"], episode["episode"])
        logging.info(f'updated entry: {episode["title"]} - {episode["episode"]}')
    exit(0)
