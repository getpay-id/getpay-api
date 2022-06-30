from app.core.pagination import Page
from app.core.router import AuthRouter

from . import schemas, views  # noqa

transaction_router = AuthRouter(prefix="/transaction", tags=["Transaction"])
transaction_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Daftar transaksi",
    response_model=Page[schemas.TransactionOut],
)
transaction_router.add_api_route(
    "/{id}",
    views.get_one,
    methods=["GET"],
    summary="Dapatkan rincian transaksi",
    response_model=schemas.TransactionOut,
)
transaction_router.add_api_route(
    "/",
    views.create,
    methods=["POST"],
    summary="Buat transaksi baru",
    response_model=schemas.TransactionOut,
)
transaction_router.add_api_route(
    "/{id}",
    views.update,
    methods=["PUT"],
    summary="Perbarui transaksi",
    response_model=schemas.UpdateTransactionOut,
)
