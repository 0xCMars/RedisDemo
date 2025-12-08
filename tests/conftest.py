import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_redis_instance():
    """Fixture that provides a mocked Redis instance"""
    mock_instance = Mock()
    mock_instance.ping.return_value = True
    mock_instance.get.return_value = None
    mock_instance.setex.return_value = True
    mock_instance.delete.return_value = 1
    return mock_instance


@pytest.fixture
def mock_redis_manager():
    """Fixture that provides a mocked RedisManager"""
    with patch('src.main.CACHE_MANAGER') as mock_manager:
        mock_manager.get.return_value = None
        mock_manager.set.return_value = True
        mock_manager.delete.return_value = None
        yield mock_manager
