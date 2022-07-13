from fastapi import FastAPI
from popol import cache, context
from popol.jobs import saq

from . import ratelimit


def init_extensions(app: FastAPI):
    context.setup(app)
    cache.setup(app)
    saq.setup(app)
    ratelimit.setup(app)
