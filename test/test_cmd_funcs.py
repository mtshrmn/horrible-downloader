import os
import sys
import pytest
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HorribleDownloader.cmd import valid_qualities, episode_filter


def test_quality_verification():
    for r in range(1, 3):
        for qualities in combinations(["480", "720", "1080"], r):
            assert valid_qualities(qualities)


def test_episode_filter_generation():
    data = [
        ("1,2,3,4", [1, 3, 4.5, 5], [1, 3]),
        ("1,3,5-7", [0.5, 1, 2, 5, 6], [1, 5, 6]),
        ("=<3,9>", [0, 0.1, 2.9, 3, 5, 9, 10.5], [0, 0.1, 2.9, 3, 10.5])
    ]
    for query, episodes, expected_output in data:
        def ep_filter(episode, filter_str=query):
            return episode_filter(episode, filter_str)
        filtered = list(filter(ep_filter, episodes))
        assert filtered == expected_output
