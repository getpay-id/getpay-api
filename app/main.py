import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import settings  # muat semua konfigurasi dari file .env
from app.core.constants import STATIC_ROOT
from app.extensions import init_extensions
from app.routers import init_routers

sentry_dsn = settings.SENTRY_DSN
if sentry_dsn:
    # reference: https://docs.sentry.io/platforms/python/guides/asgi/performance/
    traces_sample_rate = 1.0 if settings.DEBUG else 0.1
    environment = "development" if settings.DEBUG else "production"
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=traces_sample_rate,
        environment=environment,
    )

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


if sentry_dsn:
    # reference: https://philstories.medium.com/integrate-sentry-to-fastapi-7250603c070f
    @app.middleware("http")
    async def sentry_exception(request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("request", request)
                scope.user = {
                    "ip_address": request.client.host,
                }
                sentry_sdk.capture_exception(e)
            raise e
