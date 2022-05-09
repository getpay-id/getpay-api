from app.core.models import Page
from app.core.router import AuthRouter

from . import schemas, views  # noqa

method_router = AuthRouter(prefix="/method")
method_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Mendapatkan semua payment method",
    response_model=Page[schemas.PaymentMethod],
)
method_router.add_api_route(
    "/{id}",
    views.get_one,
    methods=["GET"],
    summary="Dapaatkan rincian payment method",
    response_model=schemas.PaymentMethod,
)
method_router.add_api_route(
    "/{id}",
    views.update,
    methods=["PUT"],
    summary="Perbarui payment method",
    response_model=schemas.PaymentMethod,
)
