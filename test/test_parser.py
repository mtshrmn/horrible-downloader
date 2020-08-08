import os
import sys
import pytest
from httmock import urlmatch, HTTMock
# from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HorribleDownloader import Parser

TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


@urlmatch(scheme="https", netloc="horriblesubs.info")
def shows_mock(url, request):
    path = os.path.join(TEST_DIR_PATH, "html-mocks/shows.html")
    with open(path, "r") as html:
        return html.read()


def test_get_shows():
    with HTTMock(shows_mock):
        parser = Parser()
        assert parser.shows == parser.current_shows
        assert parser.shows == {
            'Test 1': 'test-1',
            'Test 2': 'test-2',
            'Test 3': 'test-3',
            'Test 4': 'test-4',
            "Hello & World": "hello&world"
        }


def test_get_proper_title():
    with HTTMock(shows_mock):
        parser = Parser()
        reasonable_titles = [
            "Test 1",            # exact match
            "test 1",            # almost same
            "tast 1",            # typo
        ]
        for title in reasonable_titles:
            proper_title = parser.get_proper_title(title)
            assert proper_title == "Test 1"
        incorrect_titles = [
            "",                  # blank
            "random",            # non-matching text
            "123"
        ]
        for title in incorrect_titles:
            assert parser.get_proper_title(title, min_threshold=70) == ""

        assert parser.get_proper_title("Hello $amp; World") == "Hello & World"


def test_get_episodes():
    # without mocking, we'll do live testing on the website.
    parser = Parser()
    for limit in 0, 3, 11, 12, 13, 24, 28:
        title = parser.get_proper_title("one piece")
        showid = parser._get_show_id(title)
        shows_html = parser._get_html(showid, limit, "show")
        episodes = list(parser._parse_html(shows_html))
        assert len(episodes) == 12 * (((limit - 1) // 12) + 1)

        proper_get_episodes = parser.get_episodes("one piece", limit=limit)
        assert len(proper_get_episodes) == limit

        for index, episode in enumerate(proper_get_episodes):
            episode.pop("title")
            proper = episode.keys()
            non_proper = episodes[index].keys()
            error_msg = f"proper: {proper} \nnon proper: {non_proper}"
            assert episode == episodes[index], error_msg


def test_get_batches():
    parser = Parser()
    title = "Kateikyoushi Hitman Reborn!"
    batches = parser.get_batches(title)
    assert len(batches) == 2

    for batch in batches:
        assert batch["title"] == title
        has_magnet = []
        for resolution in "480", "720", "1080":
            assert resolution in batch
            has_magnet.append("Magnet" in batch[resolution])

        assert has_magnet == sorted(has_magnet, reverse=True)
        assert has_magnet[0]


def test_show_id():
    parser = Parser()
    assert parser._get_show_id("no way this will ever be an anime") == -1
