"""
Unit tests for ConfigWatcher.

Tests the file watching, debouncing, and callback functionality
of the ConfigWatcher class.
"""

import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest
import yaml

from superagi.helper.config_watcher import (
    ConfigWatcher,
    ConfigFileHandler,
    WATCHDOG_AVAILABLE,
    get_config_watcher,
    start_config_watcher,
    stop_config_watcher,
)
from superagi.helper.config_manager import ConfigManager


@pytest.fixture
def temp_config_file():
    """
    Create a temporary config file for testing.

    Yields:
        Path to the temporary config file.
    """
    config_data = {
        'DB_HOST': 'localhost',
        'DB_PORT': 5432,
        'API_KEY': 'test-api-key',
    }

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.yaml',
        delete=False
    ) as f:
        yaml.dump(config_data, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def reset_singletons(temp_config_file):
    """
    Reset singletons between tests.

    This fixture ensures each test starts with fresh instances.
    """
    # Reset global watcher
    import superagi.helper.config_watcher as watcher_module
    if watcher_module._global_watcher is not None:
        watcher_module._global_watcher.stop()
    watcher_module._global_watcher = None

    # Reset ConfigManager
    ConfigManager.reset_instance()

    yield

    # Cleanup after test
    if watcher_module._global_watcher is not None:
        watcher_module._global_watcher.stop()
    watcher_module._global_watcher = None
    ConfigManager.reset_instance()


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestConfigWatcherStartStop:
    """Tests for starting and stopping the watcher."""

    def test_watcher_start_stop(self, temp_config_file, reset_singletons):
        """Test starting and stopping the watcher."""
        watcher = ConfigWatcher(temp_config_file)

        assert watcher.is_running() is False

        # Start watcher
        success = watcher.start()
        assert success is True
        assert watcher.is_running() is True

        # Stop watcher
        watcher.stop()
        assert watcher.is_running() is False

    def test_watcher_start_twice(self, temp_config_file, reset_singletons):
        """Test that starting an already running watcher is safe."""
        watcher = ConfigWatcher(temp_config_file)

        watcher.start()
        assert watcher.is_running() is True

        # Starting again should return True but not cause issues
        success = watcher.start()
        assert success is True
        assert watcher.is_running() is True

        watcher.stop()

    def test_watcher_stop_when_not_running(self, temp_config_file, reset_singletons):
        """Test that stopping a non-running watcher is safe."""
        watcher = ConfigWatcher(temp_config_file)

        # Should not raise
        watcher.stop()
        assert watcher.is_running() is False

    def test_watcher_start_missing_file(self, reset_singletons):
        """Test starting watcher with non-existent file."""
        watcher = ConfigWatcher('/nonexistent/path/config.yaml')

        success = watcher.start()
        assert success is False
        assert watcher.is_running() is False


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestConfigWatcherFileDetection:
    """Tests for file change detection."""

    def test_watcher_detects_file_change(self, temp_config_file, reset_singletons):
        """Test that watcher detects file changes."""
        # Initialize ConfigManager with the temp file
        ConfigManager.reset_instance()
        config_manager = ConfigManager(temp_config_file)

        watcher = ConfigWatcher(temp_config_file, debounce_seconds=0.1)
        callback = MagicMock()
        watcher.register_callback(callback)

        watcher.start()
        assert watcher.is_running() is True

        # Give the watcher time to start
        time.sleep(0.2)

        # Modify the config file
        new_config = {'DB_HOST': 'newhost', 'CHANGED': True}
        with open(temp_config_file, 'w') as f:
            yaml.dump(new_config, f)

        # Wait for debounce + processing
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert callback.call_count >= 1


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestConfigWatcherDebounce:
    """Tests for debouncing functionality."""

    def test_watcher_debounces_rapid_changes(
        self, temp_config_file, reset_singletons
    ):
        """Test that rapid changes are debounced."""
        watcher = ConfigWatcher(temp_config_file, debounce_seconds=0.3)
        callback = MagicMock()
        watcher.register_callback(callback)

        watcher.start()
        time.sleep(0.1)

        # Make multiple rapid changes
        for i in range(5):
            with open(temp_config_file, 'w') as f:
                yaml.dump({'iteration': i}, f)
            time.sleep(0.05)  # 50ms between changes

        # Wait for debounce to complete
        time.sleep(0.5)

        watcher.stop()

        # Should have been debounced to fewer calls than changes
        # Due to debouncing, we expect only 1-2 calls instead of 5
        assert callback.call_count < 5


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestConfigWatcherCallbacks:
    """Tests for callback registration."""

    def test_callback_registration(self, temp_config_file, reset_singletons):
        """Test registering callbacks."""
        watcher = ConfigWatcher(temp_config_file)

        callback1 = MagicMock()
        callback2 = MagicMock()

        watcher.register_callback(callback1)
        watcher.register_callback(callback2)

        # Callbacks should not be called just by registering
        callback1.assert_not_called()
        callback2.assert_not_called()

    def test_callback_unregistration(self, temp_config_file, reset_singletons):
        """Test unregistering callbacks before starting."""
        watcher = ConfigWatcher(temp_config_file)

        callback = MagicMock()
        watcher.register_callback(callback)

        # Unregister before starting
        result = watcher.unregister_callback(callback)
        assert result is True

        # Unregister again should return False
        result = watcher.unregister_callback(callback)
        assert result is False

    def test_callback_type_validation(self, temp_config_file, reset_singletons):
        """Test that non-callable raises TypeError."""
        watcher = ConfigWatcher(temp_config_file)

        with pytest.raises(TypeError):
            watcher.register_callback("not a callable")


@pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
class TestConfigWatcherStatus:
    """Tests for status reporting."""

    def test_get_status(self, temp_config_file, reset_singletons):
        """Test get_status returns correct information."""
        watcher = ConfigWatcher(temp_config_file, debounce_seconds=2.0)

        status = watcher.get_status()

        assert isinstance(status, dict)
        assert status['running'] is False
        assert status['config_path'] == os.path.abspath(temp_config_file)
        assert status['debounce_seconds'] == 2.0
        assert status['watchdog_available'] is True
        assert status['config_exists'] is True

    def test_get_status_running(self, temp_config_file, reset_singletons):
        """Test get_status when watcher is running."""
        watcher = ConfigWatcher(temp_config_file)
        watcher.start()

        status = watcher.get_status()
        assert status['running'] is True

        watcher.stop()

        status = watcher.get_status()
        assert status['running'] is False

    def test_get_status_missing_file(self, reset_singletons):
        """Test get_status when config file doesn't exist."""
        watcher = ConfigWatcher('/nonexistent/config.yaml')

        status = watcher.get_status()
        assert status['config_exists'] is False


class TestConfigFileHandler:
    """Tests for the ConfigFileHandler class."""

    def test_handler_initialization(self, temp_config_file):
        """Test handler initialization."""
        handler = ConfigFileHandler(temp_config_file, debounce_seconds=2.0)

        assert handler.config_path == os.path.abspath(temp_config_file)
        assert handler.debounce_seconds == 2.0

    def test_handler_callback_registration(self, temp_config_file):
        """Test handler callback registration."""
        handler = ConfigFileHandler(temp_config_file)

        callback = MagicMock()
        handler.register_callback(callback)

        # Unregister
        result = handler.unregister_callback(callback)
        assert result is True

    def test_handler_cancel_pending_reload(self, temp_config_file):
        """Test canceling pending reload."""
        handler = ConfigFileHandler(temp_config_file, debounce_seconds=10.0)

        # Schedule a reload
        handler._schedule_reload()

        # Cancel it
        handler.cancel_pending_reload()

        # Should not raise
        assert True


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    def test_get_config_watcher(self, temp_config_file, reset_singletons):
        """Test get_config_watcher creates global instance."""
        watcher = get_config_watcher(temp_config_file)

        assert watcher is not None
        assert isinstance(watcher, ConfigWatcher)

        # Should return same instance
        watcher2 = get_config_watcher()
        assert watcher is watcher2

    @pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
    def test_start_config_watcher(self, temp_config_file, reset_singletons):
        """Test start_config_watcher starts global watcher."""
        success = start_config_watcher(temp_config_file)

        assert success is True

        watcher = get_config_watcher()
        assert watcher.is_running() is True

        stop_config_watcher()

    @pytest.mark.skipif(not WATCHDOG_AVAILABLE, reason="watchdog not installed")
    def test_stop_config_watcher(self, temp_config_file, reset_singletons):
        """Test stop_config_watcher stops global watcher."""
        start_config_watcher(temp_config_file)
        watcher = get_config_watcher()

        assert watcher.is_running() is True

        stop_config_watcher()

        assert watcher.is_running() is False


class TestWatchdogNotAvailable:
    """Tests for when watchdog is not installed."""

    def test_watchdog_available_flag(self):
        """Test that WATCHDOG_AVAILABLE is a boolean."""
        assert isinstance(WATCHDOG_AVAILABLE, bool)

    @pytest.mark.skipif(WATCHDOG_AVAILABLE, reason="watchdog is installed")
    def test_watcher_without_watchdog(self, temp_config_file, reset_singletons):
        """Test watcher behavior when watchdog is not available."""
        watcher = ConfigWatcher(temp_config_file)

        # Start should fail gracefully
        success = watcher.start()
        assert success is False
        assert watcher.is_running() is False
