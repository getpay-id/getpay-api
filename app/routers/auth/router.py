from fastapi import APIRouter

from . import schemas, views

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_router.add_api_route(
    "/signin",
    views.signin,
    methods=["POST"],
    summary="Dapatkan akses token",
    response_model=schemas.SuccessLogin,
)
