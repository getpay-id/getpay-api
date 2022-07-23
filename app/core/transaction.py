from popol.cache.globals import cache
from popol.jobs.saq.globals import saq_queue
from pymongo import ReturnDocument

from app import collections
from app.core import timezone
from app.core.constants import REDIS_PREFIX_TRANSACTION_CHANNEL
from app.core.enums import TransactionStatus
from app.extensions.cache_backend import RedisCache

cache: RedisCache = cache


async def paid(*, trx_id: str, message: str):
    status = TransactionStatus.paid
    trans_obj: dict = await collections.transactions.find_one_and_update(
        {"trx_id": trx_id, "__hit__": {"$exists": False}},
        {
            "$set": {
                "status": status,
                "paid_date": timezone.now(),
                "__hit__": True,
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if trans_obj and "__hit__" in trans_obj:
        print(message + ": Success.", trans_obj)
        await cache.publish(REDIS_PREFIX_TRANSACTION_CHANNEL + trx_id, status)
        await saq_queue.enqueue(
            "forward_callback", transaction_id=trx_id, status=TransactionStatus.paid
        )
    else:
        print(message + ": Fail.", trans_obj, trx_id)
