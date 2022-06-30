from fastapi import APIRouter

from . import views  # noqa
from .xendit.router import xendit_router

callback_router = APIRouter(prefix="/callback", tags=["Callback"])
callback_router.add_api_route(
    "/ipaymu", views.ipaymu, methods=["POST"], summary="Callback IPaymu"
)
callback_router.add_api_route(
    "/duitku", views.duitku, methods=["POST"], summary="Callback Duitku"
)
callback_router.include_router(xendit_router)
