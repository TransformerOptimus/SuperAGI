"""
Configuration Helper with ConfigManager Integration.

This module provides a backward-compatible interface to the configuration
system while internally using the new ConfigManager for hot-reload support.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from superagi.lib.logger import logger

# Try to import ConfigManager, fall back to legacy loading if not available
_USE_CONFIG_MANAGER = True
_config_manager_instance = None

try:
    from superagi.helper.config_manager import ConfigManager
except ImportError:
    _USE_CONFIG_MANAGER = False
    logger.warning(
        "ConfigManager not available, falling back to legacy config loading"
    )

# Legacy config storage for fallback mode
_legacy_config: Dict[str, Any] = {}
_legacy_config_loaded: bool = False


def _get_default_config_path() -> str:
    """
    Get the default path to the configuration file.

    Returns:
        The absolute path to config.yaml in the project root.
    """
    project_root = Path(__file__).parent.parent.parent
    return str(project_root / 'config.yaml')


def _load_legacy_config() -> Dict[str, Any]:
    """
    Load configuration using legacy direct YAML loading.

    This is used as a fallback when ConfigManager is not available.

    Returns:
        Dictionary containing configuration values merged with environment variables.
    """
    global _legacy_config, _legacy_config_loaded

    if _legacy_config_loaded:
        return _legacy_config

    config_path = _get_default_config_path()

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                if config_data is None:
                    config_data = {}
        else:
            logger.warning(f"Config file not found: {config_path}")
            config_data = {}

        # Merge with environment variables (env vars take precedence)
        env_vars = dict(os.environ)
        _legacy_config = {**config_data, **env_vars}
        _legacy_config_loaded = True

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse config file: {e}")
        _legacy_config = dict(os.environ)
        _legacy_config_loaded = True

    except Exception as e:
        logger.error(f"Error loading config: {e}")
        _legacy_config = dict(os.environ)
        _legacy_config_loaded = True

    return _legacy_config


def get_config_manager() -> Optional['ConfigManager']:
    """
    Get the ConfigManager singleton instance.

    Returns:
        The ConfigManager instance if available, None otherwise.

    Example:
        >>> manager = get_config_manager()
        >>> if manager:
        ...     manager.register_reload_callback(on_change)
    """
    global _config_manager_instance

    if not _USE_CONFIG_MANAGER:
        return None

    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()

    return _config_manager_instance


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a configuration value by key.

    This function maintains backward compatibility with the existing
    config system while internally using ConfigManager when available.

    Args:
        key: The configuration key to retrieve.
        default: The default value to return if the key is not found.
                Defaults to None.

    Returns:
        The configuration value if found, otherwise the default value.

    Example:
        >>> db_host = get_config('DB_HOST', 'localhost')
        >>> api_key = get_config('API_KEY')
    """
    # First check environment variables (highest priority)
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    # Use ConfigManager if available
    if _USE_CONFIG_MANAGER:
        manager = get_config_manager()
        if manager:
            return manager.get_config(key, default)

    # Fall back to legacy config loading
    config = _load_legacy_config()
    return config.get(key, default)


def reload_all_config() -> bool:
    """
    Manually trigger a configuration reload.

    This function reloads the configuration from disk. When using
    ConfigManager, it triggers a full reload including callbacks.

    Returns:
        True if configuration was reloaded successfully, False otherwise.

    Example:
        >>> if reload_all_config():
        ...     print("Configuration reloaded")
    """
    global _legacy_config_loaded

    if _USE_CONFIG_MANAGER:
        manager = get_config_manager()
        if manager:
            return manager.reload_config()

    # Legacy fallback - reset and reload
    _legacy_config_loaded = False
    _load_legacy_config()
    return True


def get_all_config() -> Dict[str, Any]:
    """
    Get all configuration values as a dictionary.

    Returns:
        A dictionary containing all configuration key-value pairs.
        Environment variables are merged with file-based configuration.

    Example:
        >>> all_config = get_all_config()
        >>> print(all_config.keys())
    """
    if _USE_CONFIG_MANAGER:
        manager = get_config_manager()
        if manager:
            # Merge with environment variables
            config = manager.get_all_config()
            return {**config, **dict(os.environ)}

    # Legacy fallback
    return _load_legacy_config().copy()


def has_config(key: str) -> bool:
    """
    Check if a configuration key exists.

    This checks both the configuration file and environment variables.

    Args:
        key: The configuration key to check.

    Returns:
        True if the key exists in configuration or environment, False otherwise.

    Example:
        >>> if has_config('DATABASE_URL'):
        ...     url = get_config('DATABASE_URL')
    """
    # Check environment first
    if key in os.environ:
        return True

    # Check ConfigManager
    if _USE_CONFIG_MANAGER:
        manager = get_config_manager()
        if manager:
            return manager.has_key(key)

    # Legacy fallback
    config = _load_legacy_config()
    return key in config


def get_config_with_env_fallback(key: str, default: Any = None) -> Any:
    """
    Get a configuration value, checking config file first, then environment.

    This differs from get_config() in that it prioritizes the config file
    over environment variables, only falling back to env if the key is
    not found in the config file.

    Args:
        key: The configuration key to retrieve.
        default: The default value if not found anywhere. Defaults to None.

    Returns:
        The configuration value from config file, environment, or default.

    Example:
        >>> # Prefers config.yaml value over environment variable
        >>> host = get_config_with_env_fallback('DB_HOST', 'localhost')
    """
    # Check ConfigManager first (config file)
    if _USE_CONFIG_MANAGER:
        manager = get_config_manager()
        if manager and manager.has_key(key):
            return manager.get_config(key)
    else:
        # Legacy fallback - check file-only config
        config_path = _get_default_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as file:
                    config_data = yaml.safe_load(file) or {}
                    if key in config_data:
                        return config_data[key]
            except Exception:
                pass

    # Then check environment
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    return default


def validate_required_config(required_keys: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required configuration keys exist.

    Args:
        required_keys: List of configuration keys that must be present.

    Returns:
        A tuple of (is_valid, missing_keys) where:
            - is_valid: True if all required keys exist, False otherwise
            - missing_keys: List of keys that are missing

    Example:
        >>> is_valid, missing = validate_required_config(['DB_HOST', 'API_KEY'])
        >>> if not is_valid:
        ...     print(f"Missing configuration: {missing}")
    """
    missing_keys = []

    for key in required_keys:
        if not has_config(key):
            missing_keys.append(key)

    is_valid = len(missing_keys) == 0
    return (is_valid, missing_keys)
