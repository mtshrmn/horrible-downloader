from configparser import ConfigParser
import os
import shutil


class ConfigManager:
    def __init__(self, conf_dir=os.path.expanduser("~/.config/horrible-downloader/")):
        self.dir = conf_dir
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        self.file = "conf.ini"
        try:
            self.conf = self._parse_conf()
        except (KeyError, ValueError, AssertionError):
            print('Invalid configuration file.')
            exit(1)

        self.quality = self.conf['settings']['resolution']
        self.download_dir = self.conf['settings']['download_dir']
        self.subscriptions = self.conf['subscriptions'].items()

    def _parse_conf(self):
        conf = ConfigParser()
        specified_conf = os.path.join(self.dir, self.file)
        success = conf.read(specified_conf)
        if not success:
            print('Couldn\'t find configuration file at specified directory.')
            print('Generating from default')
            default_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default_conf.ini')
            shutil.copyfile(default_conf, specified_conf)

        conf.read(specified_conf)

        for resolution in conf['settings']['resolution'].split(','):
            if resolution.strip() not in ('480', '720', '1080'):
                raise AssertionError
        if not isinstance(conf['settings']['download_dir'], str):
            raise AssertionError
        for sub in conf['subscriptions']:
            float(conf['subscriptions'][sub])
            # simple check to validate all of the subscriptions
        return conf
