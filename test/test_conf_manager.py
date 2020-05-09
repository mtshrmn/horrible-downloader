import os
import sys
import pytest
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HorribleDownloader import ConfigManager


data = """
[settings]
resolution = 1080, 720
download_dir = ~/videos

[subscriptions]
"""


@patch("builtins.open", mock_open(read_data=data))
@patch("os.makedirs", return_value=True)
def test_config_manager(mock_os_makedirs):
    config = ConfigManager(conf_dir="directory")
    # check if new directory was created
    assert mock_os_makedirs.called_with("directory")

    # check parsing of key elements:
    assert config.quality == "1080, 720"
    assert config.dir == "directory"
    assert config.file == "conf.ini"
    assert config.download_dir == "~/videos"
    assert dict(config.subscriptions) == {}

    # test writing abilities
    config.add_entry("test", "0")
    assert dict(config.subscriptions) == {"test": "0"}
