from configparser import ConfigParser
import os
import shutil


class ConfigManager:
    def __init__(self,
                 conf_dir=os.path.expanduser("~/.config/horrible-downloader/"),
                 file="conf.ini"):

        self.dir = conf_dir
        self.file = file
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

        try:
            self.conf = self._parse_conf()
            self.quality = self.conf['settings']['resolution']
            self.download_dir = self.conf['settings']['download_dir']
            self.subscriptions = self.conf['subscriptions']
        except (KeyError, ValueError, AssertionError):
            print('Invalid configuration file.')

    def add_entry(self, title, episode):
        entry = title.lower()
        if entry in self.subscriptions:
            return False, title

        self.update_entry(title, episode)
        return True, title

    def update_entry(self, title, episode):
        entry = title.lower()
        self.subscriptions[entry] = episode
        self.write()

    def write(self):
        # update the local file
        with open(os.path.join(self.dir, self.file), "w") as config_file:
            self.conf.write(config_file)

    def _parse_conf(self):
        conf = ConfigParser()
        specified_conf = os.path.join(self.dir, self.file)
        success = conf.read(specified_conf)
        if not success:
            print('Couldn\'t find configuration file at specified directory.')
            print('Generating from default')
            default_conf = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'default_conf.ini')
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
            # if it cant convert the value to a float,
            # it'll raise a ValueError, and we will catch it in the __init__.
        return conf
