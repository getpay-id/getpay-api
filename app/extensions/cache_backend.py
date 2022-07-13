from typing import Optional

from aioredis.client import PubSub
from popol.cache.backends.aioredis import AsyncRedisBackend


class RedisCache(AsyncRedisBackend):
    def pubsub(
        self,
        shard_hint: Optional[str] = None,
        ignore_subscribe_messages: bool = False,
    ) -> PubSub:
        return self.client.pubsub(
            shard_hint=shard_hint,
            ignore_subscribe_messages=ignore_subscribe_messages,
        )

    async def publish(self, channel: str, message: str):
        return await self.client.publish(channel, message)

    async def clear(self):
        await self.client.flushdb()
