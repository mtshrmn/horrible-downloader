from httmock import urlmatch, HTTMock
import unittest
from HorribleDownloader import Parser
import requests
from urllib.parse import parse_qs

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
            episodes = self.parser.get_episodes("enen no shouboutai", limit=4)
            self.assertEqual(len(episodes), 4)
