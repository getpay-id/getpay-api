from app.core.models import Page
from app.core.router import AuthRouter

from . import schemas, views  # noqa

gateway_router = AuthRouter(prefix="/gateway")
gateway_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Mendapatkan semua payment gateway",
    response_model=Page[schemas.PaymentGatewaySchema],
)
gateway_router.add_api_route(
    "/{id}",
    views.update,
    methods=["PUT"],
    summary="Perbarui payment gateway",
    response_model=schemas.PaymentGatewaySchema,
)
