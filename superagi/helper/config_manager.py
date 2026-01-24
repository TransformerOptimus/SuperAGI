"""
Configuration Manager with Hot-Reload Support.

This module provides a thread-safe singleton ConfigManager class that handles
configuration loading, caching, and hot-reload functionality for SuperAGI.
"""

import os
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from superagi.lib.logger import logger


class ConfigManager:
    """
    Thread-safe singleton configuration manager with hot-reload support.

    This class provides centralized configuration management with the ability
    to reload configuration at runtime without restarting the application.
    It supports callback registration for notification when config changes.

    Attributes:
        _instance: Singleton instance of ConfigManager.
        _lock: Threading lock for thread-safe operations.
        _initialized: Flag to track singleton initialization.

    Example:
        >>> config = ConfigManager()
        >>> db_host = config.get_config('DATABASE_HOST', 'localhost')
        >>> config.register_reload_callback(on_config_change)
        >>> config.reload_config()
    """

    _instance: Optional['ConfigManager'] = None
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    def __new__(cls, config_path: Optional[str] = None) -> 'ConfigManager':
        """
        Create or return the singleton instance of ConfigManager.

        Args:
            config_path: Optional path to the configuration file.
                        Defaults to 'config.yaml' in the project root.

        Returns:
            The singleton ConfigManager instance.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize the ConfigManager.

        Args:
            config_path: Optional path to the configuration file.
                        Defaults to 'config.yaml' in the project root.
        """
        with self._lock:
            if self._initialized:
                return

            self._config_lock: threading.Lock = threading.Lock()
            self._callback_lock: threading.Lock = threading.Lock()
            self._config: Dict[str, Any] = {}
            self._callbacks: List[Callable[[], None]] = []
            self._last_modified: Optional[float] = None

            if config_path is None:
                project_root = Path(__file__).parent.parent.parent
                self._config_path = str(project_root / 'config.yaml')
            else:
                self._config_path = config_path

            self._load_config()
            ConfigManager._initialized = True

    @property
    def last_modified(self) -> Optional[float]:
        """
        Get the timestamp of the last configuration file modification.

        Returns:
            The modification timestamp as a float, or None if the file
            hasn't been loaded or doesn't exist.
        """
        with self._config_lock:
            return self._last_modified

    @property
    def config_path(self) -> str:
        """
        Get the path to the configuration file.

        Returns:
            The absolute path to the configuration file.
        """
        return self._config_path

    def _load_config(self) -> bool:
        """
        Load configuration from the YAML file.

        This method reads the configuration file and parses it using
        yaml.safe_load(). It handles file not found and YAML parsing errors.

        Returns:
            True if configuration was loaded successfully, False otherwise.
        """
        try:
            if not os.path.exists(self._config_path):
                logger.warning(
                    f"Configuration file not found: {self._config_path}. "
                    "Using empty configuration."
                )
                with self._config_lock:
                    self._config = {}
                    self._last_modified = None
                return False

            file_mtime = os.path.getmtime(self._config_path)

            with open(self._config_path, 'r', encoding='utf-8') as config_file:
                loaded_config = yaml.safe_load(config_file)

            with self._config_lock:
                if loaded_config is None:
                    self._config = {}
                elif isinstance(loaded_config, dict):
                    self._config = loaded_config
                else:
                    logger.error(
                        f"Invalid configuration format in {self._config_path}. "
                        "Expected a dictionary at the root level."
                    )
                    self._config = {}
                    return False

                self._last_modified = file_mtime

            logger.info(
                f"Configuration loaded successfully from {self._config_path}"
            )
            return True

        except yaml.YAMLError as e:
            logger.error(
                f"Failed to parse YAML configuration file {self._config_path}: {e}"
            )
            with self._config_lock:
                self._config = {}
                self._last_modified = None
            return False

        except PermissionError as e:
            logger.error(
                f"Permission denied reading configuration file {self._config_path}: {e}"
            )
            with self._config_lock:
                self._config = {}
                self._last_modified = None
            return False

        except OSError as e:
            logger.error(
                f"OS error reading configuration file {self._config_path}: {e}"
            )
            with self._config_lock:
                self._config = {}
                self._last_modified = None
            return False

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.
                    Defaults to None.

        Returns:
            The configuration value if found, otherwise the default value.

        Example:
            >>> config = ConfigManager()
            >>> host = config.get_config('DATABASE_HOST', 'localhost')
        """
        with self._config_lock:
            return self._config.get(key, default)

    def reload_config(self) -> bool:
        """
        Reload configuration from the file and notify registered callbacks.

        This method reloads the configuration from disk and calls all
        registered callback functions to notify them of the change.

        Returns:
            True if configuration was reloaded successfully, False otherwise.

        Example:
            >>> config = ConfigManager()
            >>> success = config.reload_config()
            >>> if success:
            ...     print("Configuration reloaded")
        """
        logger.info("Reloading configuration...")
        success = self._load_config()

        if success:
            self._notify_callbacks()

        return success

    def get_all_config(self) -> Dict[str, Any]:
        """
        Get a copy of all configuration values.

        Returns:
            A dictionary containing all configuration key-value pairs.
            Returns a copy to prevent external modification.

        Example:
            >>> config = ConfigManager()
            >>> all_settings = config.get_all_config()
        """
        with self._config_lock:
            return self._config.copy()

    def has_key(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: The configuration key to check.

        Returns:
            True if the key exists in the configuration, False otherwise.

        Example:
            >>> config = ConfigManager()
            >>> if config.has_key('DATABASE_HOST'):
            ...     host = config.get_config('DATABASE_HOST')
        """
        with self._config_lock:
            return key in self._config

    def register_reload_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback function to be called when configuration is reloaded.

        The callback function should accept no arguments and return None.
        Callbacks are called in the order they were registered.

        Args:
            callback: A callable that takes no arguments and returns None.

        Raises:
            TypeError: If the callback is not callable.

        Example:
            >>> def on_config_change():
            ...     print("Configuration changed!")
            >>> config = ConfigManager()
            >>> config.register_reload_callback(on_config_change)
        """
        if not callable(callback):
            raise TypeError("Callback must be callable")

        with self._callback_lock:
            if callback not in self._callbacks:
                self._callbacks.append(callback)
                logger.debug(f"Registered reload callback: {callback.__name__}")

    def unregister_reload_callback(self, callback: Callable[[], None]) -> bool:
        """
        Remove a previously registered callback function.

        Args:
            callback: The callback function to remove.

        Returns:
            True if the callback was found and removed, False otherwise.

        Example:
            >>> config = ConfigManager()
            >>> config.unregister_reload_callback(on_config_change)
        """
        with self._callback_lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
                logger.debug(f"Unregistered reload callback: {callback.__name__}")
                return True
            return False

    def _notify_callbacks(self) -> None:
        """
        Notify all registered callbacks that configuration has been reloaded.

        This method calls each registered callback in order. If a callback
        raises an exception, it is logged and the remaining callbacks are
        still executed.
        """
        with self._callback_lock:
            callbacks = self._callbacks.copy()

        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(
                    f"Error executing reload callback {callback.__name__}: {e}"
                )

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance. Primarily used for testing.

        Warning:
            This method should only be used in testing scenarios.
            Using it in production code may lead to unexpected behavior.
        """
        with cls._lock:
            cls._instance = None
            cls._initialized = False
