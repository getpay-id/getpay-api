import asyncio

import async_timeout
from aioredis.client import PubSub
from bson import ObjectId
from popol.cache.globals import cache
from starlette import status
from starlette.websockets import WebSocket

from app.core.constants import REDIS_PREFIX_TRANSACTION_CHANNEL
from app.core.websocket import BaseWebSocket


async def _get_trx_id(websocket: WebSocket) -> str:
    trx_id: str = websocket.query_params.get("trx_id", None)
    if not trx_id:
        await websocket.close(status.WS_1013_TRY_AGAIN_LATER)

    if not ObjectId.is_valid(trx_id):
        await websocket.close(status.WS_1003_UNSUPPORTED_DATA)

    return trx_id


class GetTransactionStatus(BaseWebSocket):
    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        trx_id = await _get_trx_id(websocket)
        pubsub: PubSub = cache.pubsub()
        channel = REDIS_PREFIX_TRANSACTION_CHANNEL + trx_id
        await pubsub.subscribe(channel)
        websocket.state.pubsub = pubsub
        websocket.state.channel = channel
        self.task = asyncio.create_task(self.get_realtime_status(websocket))

    async def get_realtime_status(self, websocket: WebSocket):
        pubsub: PubSub = websocket.state.pubsub
        while not self.task.done():
            try:
                async with async_timeout.timeout(10):
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        trx_status = message["data"]
                        await websocket.send_text(trx_status)
                        await websocket.close()
                    await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                pass

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pubsub: PubSub = websocket.state.pubsub
        channel = websocket.state.channel
        await pubsub.unsubscribe(channel)
        self.task.cancel()
