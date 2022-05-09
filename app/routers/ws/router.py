from fastapi import APIRouter
from starlette.routing import WebSocketRoute

from . import views

ws_prefix = "/ws"
ws_routes = [WebSocketRoute(ws_prefix + "/transaction", views.GetTransactionStatus)]
ws_router = APIRouter(routes=ws_routes)
