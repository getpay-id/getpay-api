from fastapi import APIRouter, Depends

from app.core.dependencies import validate_xendit_payment

from . import views  # noqa

xendit_router = APIRouter(
    prefix="/xendit", dependencies=[Depends(validate_xendit_payment)]
)
xendit_router.add_api_route("/virtual_account", views.virtual_account, methods=["POST"])
xendit_router.add_api_route("/ewallet", views.ewallet, methods=["POST"])
xendit_router.add_api_route(
    "/convenience_store", views.convenience_store, methods=["POST"]
)
xendit_router.add_api_route("/qris", views.qris, methods=["POST"])
