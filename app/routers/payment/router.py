from typing import List

from app.core.router import AuthRouter
from app.routers.payment.channel.router import channel_router
from app.routers.payment.gateway.router import gateway_router
from app.routers.payment.method.router import method_router

from . import schemas, views  # noqa

payment_router = AuthRouter(prefix="/payment", tags=["Payment"])
payment_router.include_router(gateway_router)
payment_router.include_router(method_router)
payment_router.include_router(channel_router)
payment_router.add_api_route(
    "/active",
    views.get_all_active_payment_methods,
    methods=["GET"],
    summary="Mendapatkan semua payment method yang aktif",
    response_model=List[schemas.PublicPaymentMethodOut],
)
