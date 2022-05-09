from app import collections

from .aggregations import GET_ALL_ACTIVE_PAYMENT_METHODS


async def get_all_active_payment_methods():
    """
    Mendapatkan semua payment method yang aktif.
    """

    data = []
    async for pm_obj in collections.payment_method.aggregate(
        GET_ALL_ACTIVE_PAYMENT_METHODS
    ):
        append = True
        for d in data:
            if pm_obj.get("name") == d.get("name"):
                d["channels"].extend(pm_obj.get("channels"))
                append = False
                break
        if append:
            data.append(pm_obj)
    return data
