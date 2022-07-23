from app import collections
from app.core.enums import PaymentStatus

from . import aggregations


async def get_all_active_payment_methods():
    """
    Mendapatkan semua payment method yang aktif.
    """

    data = []
    async for pg_obj in collections.payment_gateway.find(
        {"status": PaymentStatus.active}
    ):
        pg_id = str(pg_obj["_id"])
        async for pm_obj in collections.payment_method.aggregate(
            aggregations.get_all_active_payment_methods(pg_id)
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
