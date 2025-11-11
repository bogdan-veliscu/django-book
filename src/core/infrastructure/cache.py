"""Redis cache configuration."""

import json
from typing import Any

import redis.asyncio as redis


class CacheManager:
    """Manages Redis cache connections."""

    def __init__(self, redis_url: str) -> None:
        """Initialize cache manager.

        Args:
            redis_url: The Redis connection URL.
        """
        self._redis: redis.Redis = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    @property
    def client(self) -> redis.Redis:
        """Get the Redis client."""
        return self._redis

    async def get(self, key: str) -> Any:
        """Get a value from cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found.
        """
        value = await self._redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set a value in cache.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time to live in seconds (optional).
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        if ttl:
            await self._redis.setex(key, ttl, value)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete a key from cache.

        Args:
            key: The cache key to delete.
        """
        await self._redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern.

        Args:
            pattern: The pattern to match (e.g., "user:*").
        """
        keys = []
        async for key in self._redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self._redis.delete(*keys)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache.

        Args:
            key: The cache key.

        Returns:
            True if the key exists, False otherwise.
        """
        return bool(await self._redis.exists(key))

    async def close(self) -> None:
        """Close the Redis connection."""
        await self._redis.aclose()


# Global cache manager instance (will be initialized in main.py)
cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance.

    Returns:
        The cache manager.

    Raises:
        RuntimeError: If cache manager is not initialized.
    """
    if cache_manager is None:
        raise RuntimeError("Cache manager not initialized")
    return cache_manager
