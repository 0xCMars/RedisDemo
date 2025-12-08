import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from redis.exceptions import RedisError

from src.RedisManager import RedisManager, REDIS_HOST, REDIS_PORT, CACHE_KEY_PREFIX


class TestRedisManagerInit:
    """Tests for RedisManager initialization"""

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_successful_initialization(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()

        assert manager._redis is not None
        mock_redis_instance.ping.assert_called_once()

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_failed_initialization_connection_error(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Connection refused")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()

        assert manager._redis is None

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_custom_host_port(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager(host="custom_host", port=1234)

        mock_pool.assert_called_once()
        assert mock_pool.call_args[1]['host'] == "custom_host"
        assert mock_pool.call_args[1]['port'] == 1234

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_custom_cache_key_prefix(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        custom_prefix = "custom_prefix:"
        manager = RedisManager(cache_key_prefix=custom_prefix)

        assert manager._cache_key_prefix == custom_prefix


class TestRedisManagerGet:
    """Tests for RedisManager get method"""

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_cache_hit(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        test_data = {"key": "value", "number": 123}
        mock_redis_instance.get.return_value = json.dumps(test_data)
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.get("test_key")

        assert result == test_data
        mock_redis_instance.get.assert_called_once_with(f"{CACHE_KEY_PREFIX}test_key")

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_cache_miss(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.get("nonexistent_key")

        assert result is None

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_redis_not_initialized(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.get("test_key")

        assert result is None

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_redis_error(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.side_effect = RedisError("Redis read error")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.get("test_key")

        assert result is None

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_corrupted_json(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = "invalid json {["
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.get("test_key")

        assert result is None
        mock_redis_instance.delete.assert_called_once()

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_with_custom_prefix(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        test_data = {"test": "data"}
        mock_redis_instance.get.return_value = json.dumps(test_data)
        mock_redis.return_value = mock_redis_instance

        custom_prefix = "custom:"
        manager = RedisManager(cache_key_prefix=custom_prefix)
        result = manager.get("my_key")

        mock_redis_instance.get.assert_called_once_with("custom:my_key")
        assert result == test_data


class TestRedisManagerSet:
    """Tests for RedisManager set method"""

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_success(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        test_data = {"key": "value", "number": 123}
        result = manager.set("test_key", test_data, 300)

        assert result is True
        mock_redis_instance.setex.assert_called_once()
        call_args = mock_redis_instance.setex.call_args
        assert call_args[1]['name'] == f"{CACHE_KEY_PREFIX}test_key"
        assert call_args[1]['value'] == json.dumps(test_data)
        assert call_args[1]['time'] == 300

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_default_expiration(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.set("test_key", {"data": "value"})

        assert result is True
        call_args = mock_redis_instance.setex.call_args
        assert call_args[1]['time'] == 300

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_redis_not_initialized(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.set("test_key", {"data": "value"})

        assert result is False

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_redis_error(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.side_effect = RedisError("Redis write error")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        result = manager.set("test_key", {"data": "value"})

        assert result is False

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_serialization_error(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()

        # Create an object that cannot be JSON serialized
        class NonSerializable:
            pass

        result = manager.set("test_key", NonSerializable())

        assert result is False

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_set_complex_data_structures(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        complex_data = {
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "number": 123,
            "string": "test",
            "boolean": True,
            "null": None
        }
        result = manager.set("test_key", complex_data)

        assert result is True


class TestRedisManagerDelete:
    """Tests for RedisManager delete method"""

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_delete_success(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        manager.delete("test_key")

        mock_redis_instance.delete.assert_called_once_with(f"{CACHE_KEY_PREFIX}test_key")

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_delete_redis_not_initialized(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        manager.delete("test_key")

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_delete_redis_error(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.delete.side_effect = RedisError("Redis delete error")
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        manager.delete("test_key")

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_delete_with_custom_prefix(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.delete.return_value = 1
        mock_redis.return_value = mock_redis_instance

        custom_prefix = "custom:"
        manager = RedisManager(cache_key_prefix=custom_prefix)
        manager.delete("my_key")

        mock_redis_instance.delete.assert_called_once_with("custom:my_key")


class TestRedisManagerHelpers:
    """Tests for RedisManager helper methods"""

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_full_key(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        manager = RedisManager()
        full_key = manager._get_full_key("test_key")

        assert full_key == f"{CACHE_KEY_PREFIX}test_key"

    @patch('src.RedisManager.redis.ConnectionPool')
    @patch('src.RedisManager.redis.Redis')
    def test_get_full_key_custom_prefix(self, mock_redis, mock_pool):
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance

        custom_prefix = "my_app:"
        manager = RedisManager(cache_key_prefix=custom_prefix)
        full_key = manager._get_full_key("test_key")

        assert full_key == "my_app:test_key"
