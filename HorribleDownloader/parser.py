from bs4 import BeautifulSoup
import requests
import re
from fuzzywuzzy import process as fuzzy_match


class Parser:
    def __init__(self):
        self.api = "https://horriblesubs.info/api.php"
        self.id_file = "id.json"
        self.query = {
            "method": "getshows",
            "nextid": 0
        }

    def _get_show_id(self, show: str) -> int:
        show = show.replace('&amp;', '&')
        try:
            key = fuzzy_match.extractOne(show, self.shows.keys())[0]
        except IndexError:
            return 0
        # assert the user entered a valid show name
        url = "https://horriblesubs.info/shows/" + self.shows[key]
        html = requests.get(url)
        match = re.findall("var hs_showid = \d+", html.text)
        return int(match[0].strip("var hs_showid = "))

    def _get_html(self, showid, limit, show_type="show"):
        if show_type not in ("show", "batch"):
            raise AssertionError("%s is not a valid value" % show_type)

        self.query["showid"] = showid
        self.query["nextid"] = 0
        self.query["type"] = show_type
        html = ""
        stop_text = "DONE" if show_type == "show" else "There are no batches for this show yet"

        while True:
            response = requests.get(self.api, params=self.query)
            if response.text == stop_text or self.query["nextid"] > int(limit / 12):
                break
            html += response.text
            self.query["nextid"] += 1
        return html

    @staticmethod
    def _parse_html(html):
        soup = BeautifulSoup(html, "lxml")
        episodes = soup.find_all(name="div", attrs={"class": "rls-info-container"})
        for episode in episodes:
            rls_label = episode.find(name="a", attrs={"class": "rls-label"})
            downloads = episode.find(name="div", attrs={"rls-links-container"})
            links = downloads.find_all(name="a", href=True)
            ret = {
                "title": rls_label.find(text=True, recursive=False).strip(" "),
                "episode": episode.find(name="strong").text.replace('v2', ''),
                "480": {},
                "720": {},
                "1080": {}
            }

            indexes = [x for x in ["480", "720", "1080"] for _ in range(int(len(links) / 3))]
            if not indexes:
                indexes = ["480", "720", "1080"]
            for resolution, link in zip(indexes, links):
                ret[resolution][link.text] = link["href"]

            yield ret

    @property
    def shows(self):
        ret = {}
        url = "https://horriblesubs.info/shows/"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "lxml")
        div = soup.find(name="div", attrs={"class": "shows-wrapper"})
        shows = div.find_all(name="a")
        for show in shows:
            if show["title"] == "JoJo's Bizarre Adventure - Stardust Crusaders Egypt Arc":
                href = 'jojos-bizarre-adventure-stardust-crusaders'
            else:
                href = show["href"].replace("/shows/", "")
            ret[show["title"]] = href

        return ret

    def get_episodes(self, show: str, limit=1000):
        showid = self._get_show_id(show)
        shows_html = self._get_html(showid, limit)
        return list(self._parse_html(shows_html))

    def get_batches(self, show: str):
        showid = self._get_show_id(show)
        batches_html = self._get_html(showid, 100, show_type="batch")
        return list(self._parse_html(batches_html))

    @property
    def current_shows(self):
        url = 'https://horriblesubs.info/current-season/'
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find(name="div", attrs={"class": "shows-wrapper"})
        for anime in div.find_all(name='a'):
            yield anime["title"]
