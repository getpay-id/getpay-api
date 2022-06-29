from fastapi import APIRouter, FastAPI

from app import settings

# http routers
from app.routers.apikey.router import apikey_router
from app.routers.auth.router import auth_router
from app.routers.callback.router import callback_router
from app.routers.media.router import media_router
from app.routers.payment.router import payment_router
from app.routers.transaction.router import transaction_router

# websocket routers
from app.routers.ws.router import ws_router


def init_routers(app: FastAPI):
    api = APIRouter(prefix="/" + settings.API_VERSION)
    # include all http routers
    api.include_router(auth_router)
    api.include_router(payment_router)
    api.include_router(transaction_router)
    api.include_router(apikey_router)
    api.include_router(callback_router)
    api.include_router(media_router)

    # include all websocket routers
    api.include_router(ws_router)

    # add all routers to app
    app.include_router(api)
