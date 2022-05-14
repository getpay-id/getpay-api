from bson import ObjectId
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
    else:
        print("Tidak bisa menemukan transaksi :(")
