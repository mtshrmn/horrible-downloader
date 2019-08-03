from httmock import urlmatch, HTTMock
import unittest
from HorribleDownloader import Parser
import requests

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/current-season/")
def current_season_mock(url, request):
    with open("html-mocks/shows.html", "r") as html:
        return html.read()

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/shows/")
def shows_mock(url, request):
    with open("html-mocks/shows.html", "r") as html:
        return html.read()

@urlmatch(scheme="https", netloc="horriblesubs.info", path="/api.php")
# TODO: understand how the fuck to create a mock api.
def api_mock(url, request):
    # TODO: write a response
    pass


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
