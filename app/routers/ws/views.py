from aioredis.client import PubSub
from popol.cache.globals import cache
from starlette import status
from starlette.websockets import WebSocket

from app.core.constants import REDIS_PREFIX_TRANSACTION_CHANNEL
from app.core.websocket import BaseWebSocket


class GetTransactionStatus(BaseWebSocket):
    async def on_receive(self, websocket: WebSocket, data: dict) -> None:
        if not isinstance(data, dict):
            await self.throw(websocket, status.WS_1007_INVALID_FRAME_PAYLOAD_DATA)

        trans_id = data.get("id")
        if not trans_id:
            await self.throw(websocket, status.WS_1003_UNSUPPORTED_DATA)

        pubsub: PubSub = cache.pubsub()
        async with pubsub as ps:
            channel = REDIS_PREFIX_TRANSACTION_CHANNEL + trans_id
            print("Subscribe to:", channel)
            await ps.subscribe(channel)
            message = await ps.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print(f"Message Received: {message}")
                data = message["data"]
                if data != "STOP":
                    await websocket.send_json({"status": data})
            await ps.unsubscribe(channel)
            print("Unsubscribe to:", channel)
