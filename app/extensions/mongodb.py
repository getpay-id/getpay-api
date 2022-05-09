import asyncio

from motor.core import AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient

from app import settings

client: AgnosticClient = AsyncIOMotorClient(settings.MONGODB_URI)
client.get_io_loop = asyncio.get_event_loop
getpay_db = client.getpay_db
