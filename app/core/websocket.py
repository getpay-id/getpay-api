from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

from app.core.dependencies import get_current_user_ws
from app.core.models import User


class BaseWebSocket(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()


class AuthWebSocket(BaseWebSocket):
    user: User = None

    async def on_connect(self, websocket: WebSocket):
        await super().on_connect()
        self.user = await get_current_user_ws(websocket)
        print(f"ws: {self.user} connected")

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        print(f"ws: {self.user} disconnected: {close_code!r}")
