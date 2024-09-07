from configparser import RawConfigParser
from pathlib import Path


class ConfigFile(RawConfigParser):
    """Loads given config file.

    Args:
        config_file_location (str, optional): Location of config file. Defaults to 'config.ini'.

    Raises:
        FileNotFoundError: Error if config file doesn't exist.
    """
    def __init__(self, config_file_location: str = 'config.ini'):
        super().__init__()
        if not Path(config_file_location).is_file():
            raise FileNotFoundError(f"the file {config_file_location} doesn't exist.")
        self.read(config_file_location)


config_file = ConfigFile()
