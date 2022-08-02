from fastapi import FastAPI
from popol import cache, context
from popol.jobs import saq

from . import ratelimit


def init_extensions(app: FastAPI):
    context.setup(app)
    cache.setup(app)
    saq.setup(app)
    ratelimit.setup(app)

    async def on_startup():
        # todo: hapus jika popol sudah menyediakan fitur ini
        cache_backend = app.state.cache
        await cache_backend.connect()

    app.add_event_handler("startup", on_startup)
