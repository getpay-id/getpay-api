import pickle
from datetime import timedelta
from typing import Any, Optional

from aioredis.client import PubSub

from app import settings


class PickleSerializer:
    def dumps(self, obj):
        return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

    def loads(self, data):
        return pickle.loads(data)


class Cache:
    def __init__(self, uri: str, serializer: PickleSerializer = PickleSerializer()):
        self._uri = uri
        self._serializer = serializer

    async def get(self, key: str):
        raise NotImplementedError()

    async def set(self, key: str, value):
        raise NotImplementedError()

    async def delete(self, key: str):
        raise NotImplementedError()

    async def clear(self):
        raise NotImplementedError()

    def __str__(self) -> str:
        return f"<{type(self).__name__} {self._uri}>"


class RedisCache(Cache):
    def __init__(self, uri: str, serializer: PickleSerializer = PickleSerializer()):
        try:
            import aioredis
        except ImportError:
            raise RuntimeError("aioredis is required for RedisCache")

        super().__init__(uri, serializer)
        self._redis = aioredis.from_url(uri)

    async def get(self, key: str):
        v = await self._redis.get(key)
        if v:
            v = self._serializer.loads(v)
        return v

    async def set(self, key: str, value: Any, expire: Optional[timedelta] = None):
        value = self._serializer.dumps(value)
        if expire:
            await self._redis.setex(key, int(expire.total_seconds()), value)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str):
        await self._redis.delete(key)

    def pubsub(
        self,
        shard_hint: Optional[str] = None,
        ignore_subscribe_messages: bool = False,
    ) -> PubSub:
        return self._redis.pubsub(
            shard_hint=shard_hint,
            ignore_subscribe_messages=ignore_subscribe_messages,
        )

    async def publish(self, channel: str, message: str):
        return await self._redis.publish(channel, message)

    async def clear(self):
        await self._redis.flushdb()


redis_cache = RedisCache(settings.REDIS_URL)
