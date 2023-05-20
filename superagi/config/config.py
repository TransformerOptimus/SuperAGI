import os
from pydantic import BaseSettings
from pathlib import Path
import yaml


class Config(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields

    @classmethod
    def load_config(cls, config_file: str) -> dict:
        # Fetch environment variables
        env_vars = dict(os.environ)

        # Read config file
        try:
            with open(config_file, 'r') as file:
                config_data = yaml.safe_load(file)
            if config_data is None:
                config_data = {}
        except FileNotFoundError:
            config_data = {}

        # Merge environment variables and config data
        config_data = {**config_data, **env_vars}

        return config_data

    def __init__(self, config_file: str, **kwargs):
        config_data = self.load_config(config_file)
        super().__init__(**config_data, **kwargs)

    def get_config(self, key: str, default: str = None) -> str:
        return self.dict().get(key, default)


ROOT_DIR = os.path.dirname(Path(__file__).parent.parent)
# print("root dir:", ROOT_DIR + "/config.yaml")
_config_instance = Config(ROOT_DIR + "/config.yaml")


def get_config(key: str, default: str = None) -> str:
    """
    Function to get the configuration value from the instance.

    :param key: str, the key to retrieve the configuration value.
    :param default: str, the default value to return if the key is not present.
    :return: str, the configuration value.
    """
    return _config_instance.get_config(key, default)
