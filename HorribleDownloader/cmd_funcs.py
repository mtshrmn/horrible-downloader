import os
from subprocess import call
from typing import List
from sty import fg


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
