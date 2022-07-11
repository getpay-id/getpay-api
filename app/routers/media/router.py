from app.core.models import Page
from app.core.router import AuthRouter

from . import schemas, views

media_router = AuthRouter(tags=["Media"], prefix="/media")
media_router.add_api_route(
    "/",
    views.upload,
    methods=["POST"],
    summary="Unggah file",
    response_model=schemas.MediaSchema,
)
media_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Daftar file",
    response_model=Page[schemas.MediaSchema],
)
media_router.add_api_route(
    "/{id}",
    views.get_one,
    methods=["GET"],
    summary="Dapatkan rincian file",
    response_model=schemas.MediaSchema,
)
media_router.add_api_route(
    "/{id}",
    views.update,
    methods=["POST"],
    summary="Perbarui file",
    response_model=schemas.MediaSchema,
)
media_router.add_api_route(
    "/{id}",
    views.delete,
    methods=["DELETE"],
    summary="Hapus file",
    response_model=schemas.SuccessDeleteMedia,
)
