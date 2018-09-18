from configparser import ConfigParser
import os


class ConfigManager:
    def __init__(self, conf_dir="."):
        self.dir = conf_dir
        self.file = "conf.ini"
        try:
            self.conf = self._parse_conf()
        except (KeyError, ValueError, AssertionError):
            print('Invalid configuration file.')
            exit(1)

        self.quality = self.conf['settings']['resolution']
        self.download_dir = self.conf['settings']['download_dir']
        self.subscriptions = self.conf['subscriptions']

    def _parse_conf(self):
        conf = ConfigParser()
        specified_conf = os.path.join(self.dir, self.file)
        success = conf.read(specified_conf)
        if not success:
            print('Couldn\'t find configuration file at specified directory.')
            print('Generating from default')
            default_conf = os.path.join('HorribleDownloader', 'default_conf.ini')
            with open(specified_conf, 'w') as s:
                conf.read(default_conf)
                conf.write(s)

        conf.read(specified_conf)

        assert conf['settings']['resolution'] in ('480', '720', '1080')
        assert type(conf['settings']['download_dir']) is str
        for sub in conf['subscriptions']:
            type(int(conf['subscriptions'][sub]))
            # simple check to validate all of the subscriptions
        return conf
