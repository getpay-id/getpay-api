from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import settings  # muat semua konfigurasi dari file .env
from app.core.constants import STATIC_ROOT
from app.extensions import init_extensions
from app.routers import init_routers

app = FastAPI(
    title="GetPay API", description="Your Payment Gateways Service!", version="1.0"
)
app.mount(f"/{STATIC_ROOT}", StaticFiles(directory=STATIC_ROOT), name=STATIC_ROOT)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.state.settings = settings
init_extensions(app)
init_routers(app)


@app.route("/", methods=["GET", "HEAD"], include_in_schema=False)
def index(request: Request):
    return JSONResponse({"detail": "it's alive!"})
