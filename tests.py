from httmock import urlmatch, HTTMock
import unittest
from unittest import mock
from HorribleDownloader import Parser, cmd, ConfigManager
from urllib.parse import parse_qs
import itertools

class MockedConfigParser:
    def __init__(self):
        self.conf = "TO CHANGE THE VALUE"

    def write(self, file):
        return True

    def __getitem__(self, item):
        conf = {
            "subscriptions": {
                "A": 1,
                "B": 2
            },
            "settings": {
                "resolution": "480",
                "download_dir": "download_dir"
            },
        }
        return conf[item]

class MockedConfigManager(ConfigManager):
    def _parse_conf(self):
        config = MockedConfigParser();
        return config;


@urlmatch(scheme="https", netloc="horriblesubs.info", path="/current-season/")
def current_season_mock(url, request):
    with open("html-mocks/shows.html", "r") as html:
        return html.read()

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/shows/")
def shows_mock(url, request):
    with open("html-mocks/shows.html", "r") as html:
        return html.read()

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/api.php")
def api_mock(url, request):
    query = parse_qs(url.query)
    if query["type"][0] == "show":
        with open("html-mocks/api-show.html", "r") as html:
            # Enen no Shouboutai episodes 1-4
            # showID 1274
            return html.read()
    elif query["type"][0] == "batch":
        with open("html-mocks/api-batch.html", "r") as html:
            # One Punch Man batch 1-12
            # return batch 351
            return html.read()

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/api.php")
def showid_mock(url, request):
    return "var hs_showid = 123456789"

class MockTest(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_current_season(self):
        with HTTMock(current_season_mock):
            current = self.parser.current_shows
            self.assertEqual(list(current), ["Test 1", "Test 2", "Test 3", "Test 4"])

    def test_shows_list(self):
        with HTTMock(shows_mock):
            shows = self.parser.shows
            self.assertEqual(shows, {
                'Test 1': 'test-1',
                'Test 2': 'test-2',
                'Test 3': 'test-3',
                'Test 4': 'test-4'
                })

    def test_get_episodes(self):
        with HTTMock(api_mock):
            episodes = self.parser.get_episodes("test", limit=4)
            self.assertEqual(len(episodes), 4)
            batch = self.parser.get_batches("test")
            self.assertEqual(batch[0]["title"].lower(), "one-punch man")

    def test_show_id(self):
        with HTTMock(showid_mock):
            showid = self.parser._get_show_id("doesn't matter")
            self.assertTrue(showid, 123456789)


class CMDTest(unittest.TestCase):
    def test_quality_verification(self):
        for r in range(1, 3):
            for qualities in itertools.combinations(["480", "720", "1080"], r):
                self.assertTrue(cmd.verify_quality(qualities))

    def test_episode_filter_generation(self):
        queries =  ["1,2,3,4", "1,3,5-7", "=<3,9>"]
        episodes = [[1, 3, 4.5, 5], [0.5, 1, 2, 5, 6], [0, 0.1, 0.5, 2.9, 3, 5, 9, 10.5]]
        answers =  [[1, 3], [1, 5, 6], [0, 0.1, 0.5, 2.9, 3, 10.5]]
        for q, e, a in zip(queries, episodes, answers):
            f = cmd.generate_episode_filter(q)
            filtered = list(filter(f, e))
            self.assertEqual(filtered, a)

    def test_dict_flat(self):
        o = {"foo": [1, 2, 3, 4, 5],
             "bar": ["a", "b", "c", "d"],
             "baz": [6, "e"]}
        o_flat = cmd.flatten_dict(o)
        self.assertEqual(o_flat, [5, 4, 3, 2, 1, "d", "c", "b", "a", "e", 6])

        batch = {"foo": {"baz": "bar"}}
        batch_flat = [{"baz": "bar"}]
        self.assertEqual(cmd.flatten_dict(batch), batch_flat)
