import os
from pydantic import BaseSettings
from pathlib import Path
import yaml
from superagi.lib.logger import logger

CONFIG_FILE = "config.yaml"


class Config(BaseSettings):
    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields

    @classmethod
    def load_config(cls, config_file: str) -> dict:
        # If config file exists, read it
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                config_data = yaml.safe_load(file)
            if config_data is None:
                config_data = {}
        else:
            # If config file doesn't exist, prompt for credentials and create new file
            logger.info("\033[91m\033[1m"
        + "\nConfig file not found. Enter required keys and values."
        + "\033[0m\033[0m")
            config_data = {}
            with open(config_file, "w") as file:
                yaml.dump(config_data, file, default_flow_style=False)

        # Merge environment variables and config data
        env_vars = dict(os.environ)
        config_data = {**config_data, **env_vars}

        return config_data

    def __init__(self, config_file: str, **kwargs):
        config_data = self.load_config(config_file)
        super().__init__(**config_data, **kwargs)

    def get_config(self, key: str, default: str = None) -> str:
        return self.dict().get(key, default)


ROOT_DIR = os.path.dirname(Path(__file__).parent.parent)
_config_instance = Config(ROOT_DIR + "/" + CONFIG_FILE)


def get_config(key: str, default: str = None) -> str:
    return _config_instance.get_config(key, default)