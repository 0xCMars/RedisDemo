# !/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Porject : RedisDemo
@File : RedisManager.py
@Author : MarsChen
@Date : 28/11/25 
'''
import redis
from redis.exceptions import RedisError
import json
import time
from typing import Callable, Any, Optional

# GLOBAL
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
# 默认的缓存过期时间，单位：秒
DEFAULT_EXPIRATION_SECONDS = 300
# 用于存储所有缓存键的前缀
CACHE_KEY_PREFIX = "app_cache:"

logger = logging.getLogger(__name__)

class RedisManager(object):
    """
    A generic Redis Cache Manager class, encapsulating all caching operations.
    """
    def __init__(self, host: str=REDIS_HOST, port: int=REDIS_PORT, cache_key_prefix: str=CACHE_KEY_PREFIX):
        self._redis: Optional[redis.Redis] = None
        self._cache_key_prefix = cache_key_prefix
        try:
            # Initialize Redis client with a connection pool.
            pool = redis.ConnectionPool(host=host, port=port, db=REDIS_DB, decode_responses=True)
            self._redis = redis.Redis(connection_pool=pool)
            self._redis.ping()
            logger.info("✅ RedisCacheManager: Connection established successfully.")
        except Exception as e:
            logger.error(f"❌ RedisCacheManager: Could not connect to Redis at {host}:{port}. Error: {e}.")
            self._redis = None

    def _get_full_key(self, key: str) -> str:
        """Helper function to prepend the application prefix to the key."""
        return f"{self._cache_key_prefix}{key}"

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves data from Redis for a given key.
        :param key:
        :return: The deserialized Python object, or None if the key does not exist
                    or if a read/decode error occurs.
        """
        if not self._redis:
            logger.info("redis is not init.")
            return None

        full_key = self._get_full_key(key)
        try:
            cached_data_json = self._redis.get(full_key)
            if cached_data_json:
                # Key exists, deserialize and return
                return json.loads(cached_data_json)
            # Key does not exist in Redis
            return None
        except RedisError as e:
            logger.error("Redis READ Error for key {key}: {e}. Returning None.")
            return None
        except json.JSONDecodeError as e:
            logger.error("Cache Data Corrupted for key {key}: {e}. Deleting and return None")
            self.delete(key)
            return None

    def set(self, key: str, data: Any, expire_seconds: int = DEFAULT_EXPIRATION_SECONDS) -> bool:
        """
        Writes data to Redis for a given key with an expiration time.
        :param key: the key to store
        :param data:
        :param expire_seconds: 300 mean expire after 300s
        :return: True if successful, False otherwise.
        """
        if not self._redis:
            return False

        full_key = self._get_full_key(key)

        try:
            # Convert Python object to JSON string
            data_to_cache = json.dumps(data)

            # Use SETEX for atomic setting of value and expiration time
            self._redis_client.setex(
                name=full_key,
                value=data_to_cache,
                time=expire_seconds
            )
            return True
        except RedisError as e:
            logger.error(f"Redis WRITE Error for key {key}: {e}. Write failed.")
            return False
        except Exception as e:
            # Handle serialization failure or other exceptions
            logger.error(f"Serialization error for key {key}: {e}. Write failed.")
            return False

    def delete(self, key: str) -> None:
        """
        Manually deletes a cache key.
        :param key:
        :return:
        """
        if self._redis:
            full_key = self._get_full_key(key)
            try:
                self._redis_client.delete(full_key)
                logger.info(f"Cache key {key} successfully DELETED.")
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis DELETE Error for key {key}: {e}.")