import requests
from bson import ObjectId
from popol.jobs.saq.globals import saq_queue
from pymongo import ReturnDocument

from app.core import timezone
from app.core.enums import TransactionStatus


async def update_transaction_status(ctx: dict, trx_id: str):
    """
    Perbarui status transaksi ke `TransactionStatus.expired`.
    """

    from app.collections import transactions

    trans_obj = await transactions.find_one_and_update(
        {"_id": ObjectId(trx_id), "status": TransactionStatus.pending},
        {"$set": {"status": TransactionStatus.expired, "date_updated": timezone.now()}},
        return_document=ReturnDocument.AFTER,
    )
    if trans_obj:
        print("Transaksi sudah kedaluwarsa (sukses update):", trx_id)
        await saq_queue.enqueue(
            "forward_callback", transaction_id=trx_id, status=TransactionStatus.expired
        )
    else:
        print("Tidak bisa menemukan transaksi :(")


async def forward_callback(ctx: dict, transaction_id: str, status: TransactionStatus):
    """
    Teruskan callback dari payment gateway ke server anda.
    """

    from app import settings

    url = settings.NOTIFICATION_URL
    if url:
        requests.post(
            url, json={"transaction_id": transaction_id, "status": status.value}
        )
