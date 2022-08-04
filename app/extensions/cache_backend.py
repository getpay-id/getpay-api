from typing import Optional

from popol.cache.backends.redis import AsyncRedisBackend
from redis.asyncio.client import PubSub


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
