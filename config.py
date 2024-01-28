from configparser import RawConfigParser
from pathlib import Path


class ConfigFile(RawConfigParser):
    def __init__(self, config_file: str = 'config.ini'):
        super().__init__()
        if not Path(config_file).is_file():
            print('config.ini file doesn\'t exist')
            return False
        self.read(config_file)


config_file = ConfigFile()
