from app.core.models import Page  # noqa
from app.core.router import AuthRouter

from . import schemas, views  # noqa

channel_router = AuthRouter(prefix="/channel")
channel_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Daftar payment channel",
    response_model=Page[schemas.PaymentChannel],
)
channel_router.add_api_route(
    "/{id}",
    views.get_one,
    methods=["GET"],
    summary="Dapatkan rincian payment channel",
    response_model=schemas.PaymentChannel,
)
channel_router.add_api_route(
    "/{id}",
    views.update,
    methods=["PUT"],
    summary="Perbarui payment channel",
    response_model=schemas.PaymentChannel,
)
