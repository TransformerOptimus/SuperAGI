"""
Configuration File Watcher with Hot-Reload Support.

This module provides file watching capabilities for configuration files,
enabling automatic hot-reload when changes are detected. Uses the watchdog
library for efficient file system monitoring with debouncing support.
"""

import os
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from superagi.lib.logger import logger

# Handle optional watchdog dependency gracefully
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object
    FileModifiedEvent = None
    logger.warning(
        "watchdog library not installed. Config file watching disabled. "
        "Install with: pip install watchdog"
    )


class ConfigFileHandler(FileSystemEventHandler):
    """
    File system event handler for configuration file changes.

    This handler specifically monitors for modifications to the configuration
    file and implements debouncing to prevent rapid successive reloads.

    Attributes:
        config_path: Absolute path to the configuration file being watched.
        debounce_seconds: Time in seconds to wait before triggering reload.
        _callbacks: List of callback functions to invoke on file change.
        _debounce_timer: Timer for debouncing rapid file changes.
        _timer_lock: Lock for thread-safe timer operations.
    """

    def __init__(
        self,
        config_path: str,
        debounce_seconds: float = 1.0
    ) -> None:
        """
        Initialize the configuration file handler.

        Args:
            config_path: Path to the configuration file to watch.
            debounce_seconds: Time to wait before triggering reload after
                            a change is detected. Defaults to 1.0 second.
        """
        super().__init__()
        self.config_path: str = os.path.abspath(config_path)
        self.debounce_seconds: float = debounce_seconds
        self._callbacks: List[Callable[[], None]] = []
        self._debounce_timer: Optional[threading.Timer] = None
        self._timer_lock: threading.Lock = threading.Lock()

    def on_modified(self, event) -> None:
        """
        Handle file modification events.

        This method is called when any file in the watched directory is
        modified. It filters for the specific config file and ignores
        directory events.

        Args:
            event: The file system event that occurred.
        """
        # Ignore directory events
        if event.is_directory:
            return

        # Only react to modifications of our specific config file
        event_path = os.path.abspath(event.src_path)
        if event_path != self.config_path:
            return

        logger.debug(f"Config file modification detected: {event_path}")
        self._schedule_reload()

    def _schedule_reload(self) -> None:
        """
        Schedule a debounced reload of the configuration.

        This method cancels any pending reload and schedules a new one
        after the debounce period. This prevents multiple rapid reloads
        when a file is saved multiple times in quick succession.
        """
        with self._timer_lock:
            # Cancel any existing timer
            if self._debounce_timer is not None:
                self._debounce_timer.cancel()
                self._debounce_timer = None

            # Schedule new reload
            self._debounce_timer = threading.Timer(
                self.debounce_seconds,
                self._execute_reload
            )
            self._debounce_timer.daemon = True
            self._debounce_timer.start()
            logger.debug(
                f"Scheduled config reload in {self.debounce_seconds} seconds"
            )

    def _execute_reload(self) -> None:
        """
        Execute the configuration reload and notify callbacks.

        This method is called after the debounce period has elapsed.
        It reloads the configuration via ConfigManager and notifies
        all registered callbacks.
        """
        logger.info("Executing debounced config reload")

        # Import here to avoid circular imports
        from superagi.helper.config_manager import ConfigManager

        try:
            config_manager = ConfigManager()
            success = config_manager.reload_config()

            if success:
                logger.info("Configuration reloaded successfully via watcher")
            else:
                logger.warning("Configuration reload returned failure status")

        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")

        # Notify registered callbacks
        self._notify_callbacks()

    def _notify_callbacks(self) -> None:
        """
        Notify all registered callbacks that a change was detected.

        Callbacks are called in order of registration. Exceptions in
        callbacks are caught and logged to prevent one failing callback
        from affecting others.
        """
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(
                    f"Error in config watcher callback {callback.__name__}: {e}"
                )

    def register_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback to be invoked when config file changes.

        Args:
            callback: A callable that takes no arguments and returns None.

        Raises:
            TypeError: If the callback is not callable.
        """
        if not callable(callback):
            raise TypeError("Callback must be callable")

        if callback not in self._callbacks:
            self._callbacks.append(callback)
            logger.debug(f"Registered watcher callback: {callback.__name__}")

    def unregister_callback(self, callback: Callable[[], None]) -> bool:
        """
        Remove a previously registered callback.

        Args:
            callback: The callback function to remove.

        Returns:
            True if the callback was found and removed, False otherwise.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            logger.debug(f"Unregistered watcher callback: {callback.__name__}")
            return True
        return False

    def cancel_pending_reload(self) -> None:
        """
        Cancel any pending debounced reload.

        This is useful when stopping the watcher to ensure no
        reload is triggered after the watcher has been stopped.
        """
        with self._timer_lock:
            if self._debounce_timer is not None:
                self._debounce_timer.cancel()
                self._debounce_timer = None
                logger.debug("Cancelled pending config reload")


class ConfigWatcher:
    """
    Configuration file watcher with hot-reload support.

    This class monitors a configuration file for changes and triggers
    automatic reloading when modifications are detected. It uses the
    watchdog library for efficient file system monitoring.

    Attributes:
        config_path: Path to the configuration file being watched.
        debounce_seconds: Debounce time for file change events.

    Example:
        >>> watcher = ConfigWatcher('/path/to/config.yaml')
        >>> watcher.register_callback(on_config_change)
        >>> watcher.start()
        >>> # ... later ...
        >>> watcher.stop()
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        debounce_seconds: float = 1.0
    ) -> None:
        """
        Initialize the configuration watcher.

        Args:
            config_path: Path to the configuration file to watch.
                        Defaults to 'config.yaml' in the project root.
            debounce_seconds: Time in seconds to wait before triggering
                            reload after a change. Defaults to 1.0 second.
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.config_path: str = str(project_root / 'config.yaml')
        else:
            self.config_path = os.path.abspath(config_path)

        self.debounce_seconds: float = debounce_seconds
        self._observer: Optional[Any] = None
        self._handler: Optional[ConfigFileHandler] = None
        self._running: bool = False
        self._lock: threading.Lock = threading.Lock()

    def start(self) -> bool:
        """
        Start watching the configuration file for changes.

        Returns:
            True if the watcher started successfully, False otherwise.
            Returns False if watchdog is not available or if already running.

        Example:
            >>> watcher = ConfigWatcher()
            >>> if watcher.start():
            ...     print("Watcher started")
        """
        if not WATCHDOG_AVAILABLE:
            logger.error(
                "Cannot start config watcher: watchdog library not available"
            )
            return False

        with self._lock:
            if self._running:
                logger.warning("Config watcher is already running")
                return True

            try:
                # Verify config file exists
                if not os.path.exists(self.config_path):
                    logger.error(
                        f"Cannot watch config file: {self.config_path} does not exist"
                    )
                    return False

                # Get the directory containing the config file
                watch_dir = os.path.dirname(self.config_path)
                if not watch_dir:
                    watch_dir = '.'

                # Create handler and observer
                self._handler = ConfigFileHandler(
                    self.config_path,
                    self.debounce_seconds
                )
                self._observer = Observer()
                self._observer.schedule(
                    self._handler,
                    watch_dir,
                    recursive=False
                )

                # Start observer as daemon thread
                self._observer.daemon = True
                self._observer.start()
                self._running = True

                logger.info(
                    f"Config watcher started for: {self.config_path} "
                    f"(debounce: {self.debounce_seconds}s)"
                )
                return True

            except Exception as e:
                logger.error(f"Failed to start config watcher: {e}")
                self._cleanup()
                return False

    def stop(self) -> None:
        """
        Stop watching the configuration file.

        This method safely stops the observer thread and cancels any
        pending debounced reloads.

        Example:
            >>> watcher.stop()
        """
        with self._lock:
            if not self._running:
                logger.debug("Config watcher is not running")
                return

            logger.info("Stopping config watcher...")
            self._cleanup()
            logger.info("Config watcher stopped")

    def _cleanup(self) -> None:
        """
        Clean up watcher resources.

        This internal method stops the observer, cancels pending reloads,
        and resets internal state.
        """
        if self._handler is not None:
            self._handler.cancel_pending_reload()

        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=5.0)
            except Exception as e:
                logger.error(f"Error stopping observer: {e}")

        self._observer = None
        self._handler = None
        self._running = False

    def is_running(self) -> bool:
        """
        Check if the watcher is currently active.

        Returns:
            True if the watcher is running, False otherwise.
        """
        with self._lock:
            return self._running

    def register_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback to be invoked when the config file changes.

        The callback will be called after the configuration has been
        reloaded. Multiple callbacks can be registered and will be
        called in order of registration.

        Args:
            callback: A callable that takes no arguments and returns None.

        Raises:
            TypeError: If the callback is not callable.
            RuntimeError: If the watcher has not been started.

        Example:
            >>> def on_change():
            ...     print("Config changed!")
            >>> watcher.register_callback(on_change)
        """
        if not callable(callback):
            raise TypeError("Callback must be callable")

        with self._lock:
            if self._handler is None:
                # Create handler even if not started yet
                if not hasattr(self, '_pending_callbacks'):
                    self._pending_callbacks: List[Callable[[], None]] = []
                self._pending_callbacks.append(callback)
                logger.debug(
                    f"Queued callback for when watcher starts: {callback.__name__}"
                )
            else:
                self._handler.register_callback(callback)

    def unregister_callback(self, callback: Callable[[], None]) -> bool:
        """
        Remove a previously registered callback.

        Args:
            callback: The callback function to remove.

        Returns:
            True if the callback was found and removed, False otherwise.
        """
        with self._lock:
            if self._handler is not None:
                return self._handler.unregister_callback(callback)

            if hasattr(self, '_pending_callbacks'):
                if callback in self._pending_callbacks:
                    self._pending_callbacks.remove(callback)
                    return True
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the watcher.

        Returns:
            A dictionary containing:
                - running: Whether the watcher is active
                - config_path: Path to the watched config file
                - debounce_seconds: Current debounce setting
                - watchdog_available: Whether watchdog library is installed
                - config_exists: Whether the config file exists

        Example:
            >>> status = watcher.get_status()
            >>> print(f"Running: {status['running']}")
        """
        with self._lock:
            return {
                'running': self._running,
                'config_path': self.config_path,
                'debounce_seconds': self.debounce_seconds,
                'watchdog_available': WATCHDOG_AVAILABLE,
                'config_exists': os.path.exists(self.config_path)
            }


# Global watcher instance for convenience functions
_global_watcher: Optional[ConfigWatcher] = None
_global_watcher_lock: threading.Lock = threading.Lock()


def get_config_watcher(config_path: Optional[str] = None) -> ConfigWatcher:
    """
    Get or create the global ConfigWatcher instance.

    This function provides a convenient way to access a singleton-like
    global watcher instance. If a watcher doesn't exist, one is created
    with the specified config path.

    Args:
        config_path: Path to the configuration file. Only used when
                    creating a new watcher instance.

    Returns:
        The global ConfigWatcher instance.

    Example:
        >>> watcher = get_config_watcher('/path/to/config.yaml')
        >>> watcher.start()
    """
    global _global_watcher

    with _global_watcher_lock:
        if _global_watcher is None:
            _global_watcher = ConfigWatcher(config_path)
        return _global_watcher


def start_config_watcher(config_path: Optional[str] = None) -> bool:
    """
    Start the global configuration watcher.

    This is a convenience function that creates (if necessary) and
    starts the global ConfigWatcher instance.

    Args:
        config_path: Path to the configuration file. Only used when
                    creating a new watcher instance.

    Returns:
        True if the watcher started successfully, False otherwise.

    Example:
        >>> if start_config_watcher():
        ...     print("Config watching enabled")
    """
    watcher = get_config_watcher(config_path)
    return watcher.start()


def stop_config_watcher() -> None:
    """
    Stop the global configuration watcher.

    This is a convenience function that stops the global ConfigWatcher
    instance if one exists and is running.

    Example:
        >>> stop_config_watcher()
    """
    global _global_watcher

    with _global_watcher_lock:
        if _global_watcher is not None:
            _global_watcher.stop()
