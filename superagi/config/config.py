import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from superagi.lib.logger import logger

CONFIG_FILE = "config.yaml"


class Config(BaseSettings):
    """Modern configuration management using Pydantic v2."""
    
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    # Database configuration
    db_name: str = Field(default="super_agi_main", alias="DB_NAME")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_username: str = Field(default="superagi", alias="DB_USERNAME")
    db_password: str = Field(default="password", alias="DB_PASSWORD")
    db_url: str = Field(default="postgresql://superagi:password@localhost:5432/super_agi_main", alias="DB_URL")
    
    # Redis configuration
    redis_url: str = Field(default="localhost:6379", alias="REDIS_URL")
    
    # API Keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    pinecone_api_key: str = Field(default="", alias="PINECONE_API_KEY")
    pinecone_environment: str = Field(default="", alias="PINECONE_ENVIRONMENT")
    
    # Model configuration
    model_name: str = Field(default="gpt-3.5-turbo", alias="MODEL_NAME")
    max_model_token_limit: int = Field(default=4032, alias="MAX_MODEL_TOKEN_LIMIT")
    
    # Storage configuration
    storage_type: str = Field(default="FILE", alias="STORAGE_TYPE")
    
    # Environment
    env: str = Field(default="DEV", alias="ENV")
    jwt_secret_key: str = Field(default="secret", alias="JWT_SECRET_KEY")

    @classmethod
    def load_from_yaml(cls, config_file: str) -> "Config":
        """Load configuration from YAML file and environment variables."""
        config_data = {}
        
        # Load from YAML file if it exists
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                if yaml_data:
                    config_data.update(yaml_data)
        else:
            logger.info(
                "\033[91m\033[1m"
                "\nConfig file not found. Using environment variables and defaults."
                "\033[0m\033[0m"
            )
            # Create empty config file for future use
            with open(config_file, "w", encoding="utf-8") as file:
                yaml.dump({}, file, default_flow_style=False)

        # Environment variables take precedence
        return cls(**config_data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(self, key.lower(), default)


# Global configuration instance
ROOT_DIR = Path(__file__).parent.parent.parent
_config_instance = Config.load_from_yaml(ROOT_DIR / CONFIG_FILE)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value from global instance."""
    return _config_instance.get(key, default)