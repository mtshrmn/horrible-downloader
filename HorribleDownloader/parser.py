from bs4 import BeautifulSoup
import requests
import re
from rapidfuzz import process, fuzz
from typing import Iterable


class Parser:
    def __init__(self):
        # because this data won't change as often
        # we can populate it once when initiating the parser
        # this will reduce overall running time.
        # the only downside is slow initiation (around 1s)
        self.shows = self._get_shows("shows")
        self.current_shows = self._get_shows("current-season")

    def get_proper_title(self, title: str, min_threshold=0) -> str:
        # because we're dealing with html, there will be character references.
        # there might be other references other than the ampersand.
        title = title.replace("&amp;", "&")
        proper_title, ratio = process.extractOne(title, self.shows.keys(), scorer=fuzz.token_set_ratio)
        # if the proper_title is too different than the title, return "".
        if ratio <= min_threshold:
            return ""
        return proper_title

    def get_episodes(self, show: str, limit=1000, batches=False) -> list:
        if batches:
            return self.get_batches(show, limit=limit)
        return self._get_uris(show, "show", limit)

    def get_batches(self, show: str, limit=1000) -> list:
        return self._get_uris(show, "batch", limit)

    @staticmethod
    def _get_shows(page: str) -> dict:
        # instead of writing two identical functions (shows, current_shows),
        # we have one function that parses the data from the given page.
        # shows: https://horriblesubs.info/shows/
        # current_shows: https://horriblesubs.info/current-season/
        ret = {}
        url = f"https://horriblesubs.info/{page}/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "lxml")
        div = soup.find("div", {"class": "shows-wrapper"})
        shows = div.find_all("a")
        for show in shows:
            # each URI starts with `/shows/`, we will remove it here,
            # but we must append it later.
            href = show["href"].replace("/shows/", "")
            ret[show["title"]] = href

        # the return dictionary will have the titles as keys and URIs as values.
        return ret

    @staticmethod
    def _get_html(showid: int, limit: int, show_type: str) -> str:
        # another thing to note - the horriblesubs api runs in reverse
        # which means the first element will be the most recent episode
        # that guarantees us that the first episode will be the last element.1
        api = "https://horriblesubs.info/api.php"
        # the horriblesubs api returns html to be inserted directly into the site,
        # because the api works with pagination
        # we have a blank html variable that we'll append data onto.
        html = ""
        # the pagination is controlled by the `nextid` parameter.
        # if there are episodes, it will return the html,
        # otherwise it will return an end string (stop_text)
        # the end string is different for regular episodes and for batches
        show_stop_text = "DONE"
        batch_stop_text = "There are no batches for this show yet"
        stop_text = show_stop_text if show_type == "show" else batch_stop_text
        query = {
            "method": "getshows",
            "showid": showid,
            "nextid": 0,
            "type": show_type
        }
        # our python wrapper doesn't use pagination, so it must run over all the pages.
        # because some shows have a huge amount of episodes
        # we want to specify a limit for the amount.
        # sometimes we just care about the most recent episode.
        while True:
            response = requests.get(api, params=query)
            # the limit is counted in number of episodes (or batches)
            # because each page contains 12 episodes, we must divide it by 12.
            if response.text == stop_text or query["nextid"] > (limit - 1) // 12:
                break
            html += response.text
            query["nextid"] += 1
        # once all the pages were appended, return it as raw data to be parsed.
        return html

    @staticmethod
    def _parse_html(html: str) -> Iterable[dict]:
        soup = BeautifulSoup(html, "lxml")
        episodes = soup.find_all("div", {"class": "rls-info-container"})

        for episode in episodes:
            downloads = episode.find("div", {"class": "rls-links-container"})
            links = downloads.find_all("a", href=True)
            # the episode object, for now, we only know the episode number
            # all that is left is to add the URIs
            ret = {
                "episode": episode.find("strong").text.replace('v2', ''),
                "480": {},
                "720": {},
                "1080": {}
            }

            # ____populate the URIs____
            # the links are as follows:
            # [Magnet, Torrent, XDCC, Uploaded.net, FileUpload, Uplod] * 3
            # sometimes, not all links exist, and not always all resoultions exist.
            # the premise is:
            # 1. each resolution has a magnet link (the text is: "Magnet").
            # 2. the magnet link will be the first link for each resolution.
            # 3. the resolutions start from low to high.
            resolutions = iter(["480", "720", "1080"])
            for link in links:
                # this is always true on the first iteration
                if link.text == "Magnet":
                    resolution = next(resolutions)
                ret[resolution][link.text] = link["href"]

            yield ret

    def _get_show_id(self, title: str) -> int:
        # the horriblesubs api works with shows id
        # the id is a numeric value based on the order it was added to the site.
        # because the api is not meant to be public,
        # there's no easy way to retrieve the id.
        # the id appears in a script tag inside of the html of the show page.
        # var hs_showid = ID
        # because the task is simple, we dont need BeautifulSoup for that
        try:
            url = "https://horriblesubs.info/shows/" + self.shows[title]
            html = requests.get(url)
            match = re.findall(r"var hs_showid = \d+", html.text)
            return int(match[0].strip("var hs_showid = "))
        except KeyError:
            # if no id was found, return default value
            return -1

    def _get_uris(self, show: str, show_type: str, limit: int) -> list:
        title = self.get_proper_title(show)
        showid = self._get_show_id(title)
        shows_html = self._get_html(showid, limit, show_type)
        # as discussed in https://github.com/Jelomite/horrible-downloader/issues/24
        # to reduce confusion, the length of episodes should be equal to the limit
        episodes = list(self._parse_html(shows_html))[:limit]
        # for each episode, append a title argument.
        # it's not ideal. it's for backward compatibility.
        # TODO: remove this in veriosn 2.0
        for episode in episodes:
            episode.update({"title": title})
        return episodes
