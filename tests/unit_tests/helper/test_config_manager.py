"""
Unit tests for ConfigManager.

Tests the singleton pattern, configuration loading, reloading,
and callback functionality of the ConfigManager class.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

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
        'DEBUG': True,
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
def reset_config_manager():
    """
    Reset ConfigManager singleton between tests.

    This fixture ensures each test starts with a fresh ConfigManager instance.
    """
    ConfigManager.reset_instance()
    yield
    ConfigManager.reset_instance()


class TestConfigManagerSingleton:
    """Tests for the singleton pattern implementation."""

    def test_singleton_pattern(self, temp_config_file, reset_config_manager):
        """Verify that ConfigManager returns the same instance."""
        manager1 = ConfigManager(temp_config_file)
        manager2 = ConfigManager(temp_config_file)

        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    def test_singleton_maintains_state(self, temp_config_file, reset_config_manager):
        """Verify that singleton maintains state across instances."""
        manager1 = ConfigManager(temp_config_file)
        original_path = manager1.config_path

        manager2 = ConfigManager()  # Called without path
        assert manager2.config_path == original_path


class TestConfigManagerGetConfig:
    """Tests for the get_config method."""

    def test_get_config_existing_key(self, temp_config_file, reset_config_manager):
        """Test getting a configuration key that exists."""
        manager = ConfigManager(temp_config_file)

        assert manager.get_config('DB_HOST') == 'localhost'
        assert manager.get_config('DB_PORT') == 5432
        assert manager.get_config('API_KEY') == 'test-api-key'
        assert manager.get_config('DEBUG') is True

    def test_get_config_missing_key_with_default(
        self, temp_config_file, reset_config_manager
    ):
        """Test getting a missing key with a default value."""
        manager = ConfigManager(temp_config_file)

        result = manager.get_config('NONEXISTENT_KEY', 'default_value')
        assert result == 'default_value'

        result_int = manager.get_config('MISSING_PORT', 8080)
        assert result_int == 8080

    def test_get_config_missing_key_no_default(
        self, temp_config_file, reset_config_manager
    ):
        """Test getting a missing key without a default returns None."""
        manager = ConfigManager(temp_config_file)

        result = manager.get_config('NONEXISTENT_KEY')
        assert result is None

    def test_get_all_config(self, temp_config_file, reset_config_manager):
        """Test getting all configuration values."""
        manager = ConfigManager(temp_config_file)
        all_config = manager.get_all_config()

        assert isinstance(all_config, dict)
        assert 'DB_HOST' in all_config
        assert 'DB_PORT' in all_config
        assert all_config['DB_HOST'] == 'localhost'

    def test_has_key(self, temp_config_file, reset_config_manager):
        """Test checking if a key exists."""
        manager = ConfigManager(temp_config_file)

        assert manager.has_key('DB_HOST') is True
        assert manager.has_key('NONEXISTENT') is False


class TestConfigManagerReload:
    """Tests for the reload_config method."""

    def test_reload_config_success(self, temp_config_file, reset_config_manager):
        """Test successful configuration reload."""
        manager = ConfigManager(temp_config_file)

        # Modify the config file
        new_config = {'DB_HOST': 'newhost', 'NEW_KEY': 'new_value'}
        with open(temp_config_file, 'w') as f:
            yaml.dump(new_config, f)

        # Reload and verify
        success = manager.reload_config()
        assert success is True
        assert manager.get_config('DB_HOST') == 'newhost'
        assert manager.get_config('NEW_KEY') == 'new_value'
        assert manager.get_config('DB_PORT') is None  # Old key removed

    def test_reload_config_file_not_found(self, reset_config_manager):
        """Test handling of missing configuration file during reload."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            yaml.dump({'key': 'value'}, f)
            temp_path = f.name

        manager = ConfigManager(temp_path)
        assert manager.get_config('key') == 'value'

        # Delete the file
        os.unlink(temp_path)

        # Reload should handle missing file gracefully
        success = manager.reload_config()
        assert success is False

    def test_reload_config_invalid_yaml(self, temp_config_file, reset_config_manager):
        """Test handling of invalid YAML during reload."""
        manager = ConfigManager(temp_config_file)

        # Write invalid YAML
        with open(temp_config_file, 'w') as f:
            f.write('invalid: yaml: content: [')

        # Reload should handle invalid YAML gracefully
        success = manager.reload_config()
        assert success is False


class TestConfigManagerCallbacks:
    """Tests for the callback registration and execution."""

    def test_callback_registration(self, temp_config_file, reset_config_manager):
        """Test registering callbacks."""
        manager = ConfigManager(temp_config_file)

        callback1 = MagicMock()
        callback2 = MagicMock()

        manager.register_reload_callback(callback1)
        manager.register_reload_callback(callback2)

        # Registering same callback again should not duplicate
        manager.register_reload_callback(callback1)

        # Verify callbacks are not called just by registering
        callback1.assert_not_called()
        callback2.assert_not_called()

    def test_callback_unregistration(self, temp_config_file, reset_config_manager):
        """Test unregistering callbacks."""
        manager = ConfigManager(temp_config_file)

        callback = MagicMock()
        manager.register_reload_callback(callback)

        # Unregister should return True for registered callback
        result = manager.unregister_reload_callback(callback)
        assert result is True

        # Unregister again should return False
        result = manager.unregister_reload_callback(callback)
        assert result is False

    def test_callback_execution_on_reload(
        self, temp_config_file, reset_config_manager
    ):
        """Test that callbacks are called on configuration reload."""
        manager = ConfigManager(temp_config_file)

        callback1 = MagicMock()
        callback2 = MagicMock()

        manager.register_reload_callback(callback1)
        manager.register_reload_callback(callback2)

        # Reload configuration
        manager.reload_config()

        # Both callbacks should have been called
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_callback_exception_handling(
        self, temp_config_file, reset_config_manager
    ):
        """Test that callback exceptions don't prevent other callbacks."""
        manager = ConfigManager(temp_config_file)

        callback1 = MagicMock(side_effect=Exception("Test error"))
        callback2 = MagicMock()

        manager.register_reload_callback(callback1)
        manager.register_reload_callback(callback2)

        # Reload should not raise, and second callback should still run
        manager.reload_config()

        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_callback_type_validation(self, temp_config_file, reset_config_manager):
        """Test that non-callable raises TypeError."""
        manager = ConfigManager(temp_config_file)

        with pytest.raises(TypeError):
            manager.register_reload_callback("not a callable")

        with pytest.raises(TypeError):
            manager.register_reload_callback(123)


class TestConfigManagerProperties:
    """Tests for ConfigManager properties."""

    def test_config_path_property(self, temp_config_file, reset_config_manager):
        """Test the config_path property."""
        manager = ConfigManager(temp_config_file)
        assert manager.config_path == temp_config_file

    def test_last_modified_property(self, temp_config_file, reset_config_manager):
        """Test the last_modified property."""
        manager = ConfigManager(temp_config_file)

        # Should have a modification time after loading
        assert manager.last_modified is not None
        assert isinstance(manager.last_modified, float)

        # Should update after reload
        old_mtime = manager.last_modified

        # Touch the file to update mtime
        with open(temp_config_file, 'a') as f:
            f.write('\n')

        manager.reload_config()
        assert manager.last_modified >= old_mtime


class TestConfigManagerEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_config_file(self, reset_config_manager):
        """Test handling of empty configuration file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            f.write('')
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            assert manager.get_all_config() == {}
            assert manager.get_config('any_key', 'default') == 'default'
        finally:
            os.unlink(temp_path)

    def test_config_with_nested_values(self, reset_config_manager):
        """Test handling of nested configuration values."""
        config_data = {
            'database': {
                'host': 'localhost',
                'port': 5432,
            },
            'api': {
                'key': 'test-key',
                'timeout': 30,
            }
        }

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            db_config = manager.get_config('database')
            assert db_config['host'] == 'localhost'
            assert db_config['port'] == 5432
        finally:
            os.unlink(temp_path)

    def test_reset_instance(self, temp_config_file):
        """Test that reset_instance properly resets the singleton."""
        manager1 = ConfigManager(temp_config_file)
        ConfigManager.reset_instance()

        # Create new instance with different path
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.yaml', delete=False
        ) as f:
            yaml.dump({'different': 'config'}, f)
            new_path = f.name

        try:
            manager2 = ConfigManager(new_path)
            assert manager1 is not manager2
            assert manager2.get_config('different') == 'config'
        finally:
            os.unlink(new_path)
            ConfigManager.reset_instance()
