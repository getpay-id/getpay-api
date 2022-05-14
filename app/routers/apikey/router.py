from fastapi import APIRouter, Depends

from app.core.dependencies import jwt_required
from app.core.models import Page

from . import schemas, views

apikey_router = APIRouter(
    prefix="/apikey",
    tags=["API Key"],
    dependencies=[Depends(jwt_required)],
)
apikey_router.add_api_route(
    "/",
    views.create,
    methods=["POST"],
    summary="Buat API Key baru",
    response_model=schemas.APIKeyDetail,
)
apikey_router.add_api_route(
    "/{id}",
    views.get_one,
    methods=["GET"],
    summary="Dapatkan rincian API Key",
    response_model=schemas.PublicAPIKey,
)
apikey_router.add_api_route(
    "/",
    views.get_all,
    methods=["GET"],
    summary="Mendapatkan semua API Key",
    response_model=Page[schemas.PublicAPIKey],
)
apikey_router.add_api_route(
    "/{id}", views.delete, methods=["DELETE"], summary="Hapus API Key"
)
