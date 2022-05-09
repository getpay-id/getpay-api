from typing import Callable, Dict, Union

from starlette import status
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.core.dependencies import get_current_user_ws
from app.core.enums import WebSocketMediaType
from app.core.models import User


def _validator_media_type(expected_type: type) -> Callable[[WebSocket, dict], None]:
    async def _validator(websocket: WebSocket, data: dict) -> None:
        if not isinstance(data, expected_type):
            code = status.WS_1003_UNSUPPORTED_DATA
            raise WebSocketDisconnect(code)

    return _validator


class BaseWebSocket(WebSocketEndpoint):
    encoding = "json"
    media_type: WebSocketMediaType = WebSocketMediaType.dictionary
    media_handlers: Dict[str, Callable[[WebSocket, dict], None]] = {
        WebSocketMediaType.dictionary: _validator_media_type(dict),
        WebSocketMediaType.array: _validator_media_type(list),
    }

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: Union[dict, list]) -> None:
        func = self.media_handlers[self.media_type]
        await func(websocket, data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        print(f"{self.user} disconnected: {close_code!r}")

    async def throw(self, websocket: WebSocket, code: int):
        await websocket.close(code)
        raise WebSocketDisconnect(code)


class AuthWebSocket(BaseWebSocket):
    user: User = None

    async def on_connect(self, websocket: WebSocket):
        await super().on_connect()
        self.user = await get_current_user_ws(websocket)
        print(f"{self.user} connected")
