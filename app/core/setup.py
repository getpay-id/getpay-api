from pymongo.results import DeleteResult, InsertOneResult

from app import collections, settings
from app.core import timezone
from app.core.constants import (
    DUITKU_EWALLET,
    DUITKU_QRIS,
    DUITKU_RETAIL_OUTLET,
    DUITKU_VIRTUAL_ACCOUNTS,
    IPAYMU_CONVENIENCE_STORES,
    IPAYMU_QRIS,
    IPAYMU_VIRTUAL_ACCOUNTS,
    MIN_AMOUNT_PAYMENT_METHODS,
    PAYMENT_METHODS,
    UNUSED_PAYMENT_METHODS,
    XENDIT_CONVENIENCE_STORES,
    XENDIT_EWALLET,
    XENDIT_QRIS,
)
from app.core.enums import PaymentGateway, PaymentMethod, PaymentStatus
from app.core.thirdparty import xendit
from app.core.utils import generate_random_string


async def get_or_create_payment_gateway(name: PaymentGateway) -> str:
    pg_obj = await collections.payment_gateway.find_one({"name": name.value})
    if not pg_obj:
        result: InsertOneResult = await collections.payment_gateway.insert_one(
            {
                "name": name.value,
                "status": PaymentStatus.active,
                "date_created": timezone.now(),
                "date_updated": None,
            }
        )
        pg_id = str(result.inserted_id)
    else:
        pg_id = str(pg_obj["_id"])

    return pg_id


async def install_payment_gateway(name: PaymentGateway):
    print(f"Installing payment gateway {name!r}...")
    pg_id = await get_or_create_payment_gateway(name)
    await create_payment_methods(pg_id, name)


async def get_or_create_payment_method(pg_id: str, pm_code: PaymentMethod) -> str:
    pm_obj = await collections.payment_method.find_one(
        {"pg_id": pg_id, "code": pm_code.value}
    )
    if not pm_obj:
        pm_name = PAYMENT_METHODS[pm_code]
        pm_obj: InsertOneResult = await collections.payment_method.insert_one(
            {
                "pg_id": pg_id,
                "code": pm_code.value,
                "name": pm_name,
                "status": PaymentStatus.active,
                "date_created": timezone.now(),
                "date_updated": None,
            }
        )
        pm_id = pm_obj.inserted_id
        print(f" + Payment method {pm_name!r} created")
    else:
        pm_id = str(pm_obj["_id"])
        print(f" + Payment method {pm_obj['name']!r} already exists")

    return str(pm_id)


async def create_payment_methods(pg_id: str, name: PaymentGateway):
    for pm_code in PaymentMethod:
        if name == PaymentGateway.ipaymu:
            if pm_code in (PaymentMethod.ewallet, PaymentMethod.bank_transfer):
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            payment_data = {}
            if pm_code == PaymentMethod.va:
                payment_data = IPAYMU_VIRTUAL_ACCOUNTS

            elif pm_code == PaymentMethod.cstore:
                payment_data = IPAYMU_CONVENIENCE_STORES

            elif pm_code == PaymentMethod.qris:
                payment_data = IPAYMU_QRIS

            for (
                channel_code,
                channel_name,
            ) in payment_data.items():
                min_amount = get_min_amount_payment_method(name, pm_code, channel_code)
                await create_payment_channel(
                    pm_id, channel_name, channel_code, min_amount=min_amount
                )

        elif name == PaymentGateway.xendit:
            if pm_code == PaymentMethod.bank_transfer:
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            payment_data = {}
            va_status = {}
            if pm_code == PaymentMethod.va:
                va_banks = xendit.get_virtual_account_banks(settings.XENDIT_API_KEY)
                for bank in va_banks:
                    channel_name = bank.name
                    channel_code = bank.code
                    payment_data[channel_code] = channel_name
                    status = (
                        PaymentStatus.active
                        if getattr(bank, "is_activated", False)
                        else PaymentStatus.inactive
                    )
                    va_status[channel_code] = status

            elif pm_code == PaymentMethod.cstore:
                payment_data = XENDIT_CONVENIENCE_STORES

            elif pm_code == PaymentMethod.qris:
                payment_data = XENDIT_QRIS

            elif pm_code == PaymentMethod.ewallet:
                payment_data = XENDIT_EWALLET

            for channel_code, channel_name in payment_data.items():
                status = va_status.get(channel_code) or PaymentStatus.active
                min_amount = get_min_amount_payment_method(name, pm_code, channel_code)
                await create_payment_channel(
                    pm_id,
                    channel_name,
                    channel_code,
                    status=status,
                    min_amount=min_amount,
                )

        elif name == PaymentGateway.duitku:
            if pm_code == PaymentMethod.bank_transfer:
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            payment_data = {}
            if pm_code == PaymentMethod.va:
                payment_data = DUITKU_VIRTUAL_ACCOUNTS

            elif pm_code == PaymentMethod.cstore:
                payment_data = DUITKU_RETAIL_OUTLET

            elif pm_code == PaymentMethod.qris:
                payment_data = DUITKU_QRIS

            elif pm_code == PaymentMethod.ewallet:
                payment_data = DUITKU_EWALLET

            for channel_code, channel_name in payment_data.items():
                min_amount = get_min_amount_payment_method(name, pm_code, channel_code)
                await create_payment_channel(
                    pm_id, channel_name, channel_code, min_amount=min_amount
                )


def get_min_amount_payment_method(
    payment_gateway: PaymentGateway, payment_method: PaymentMethod, channel_code: str
) -> int:
    for pg, pm_dict in MIN_AMOUNT_PAYMENT_METHODS.items():
        if pg == payment_gateway:
            pm_data = pm_dict.get(payment_method) or {}
            value = pm_data.get(channel_code)
            if value is not None:
                return value
    return 0


async def create_payment_channel(
    pm_id: str,
    channel_name: str,
    channel_code: str,
    *,
    status: PaymentStatus = PaymentStatus.active,
    min_amount: int = 0,
):
    channel_obj = await collections.payment_channel.find_one(
        {"pm_id": pm_id, "code": channel_code}
    )
    if not channel_obj:
        channel_obj: InsertOneResult = await collections.payment_channel.insert_one(
            {
                "pm_id": pm_id,
                "code": channel_code,
                "name": channel_name,
                "unique_code": generate_random_string(length=6),
                "fee": 0,
                "fee_percent": 0.0,
                "img": None,
                "status": int(status),
                "min_amount": min_amount,
                "date_created": timezone.now(),
                "date_updated": None,
            }
        )
        print(f"  * Payment channel: {channel_name} created")
    else:
        print(f"  ! Payment channel: {channel_obj['name']} already exists")
        new_fields = {"min_amount": min_amount}
        for k in new_fields.copy().keys():
            if k in channel_obj:
                new_fields.pop(k)

        if new_fields:
            print(f"  * added a new field to the payment channel collection...")
            channel_obj = await collections.payment_channel.update_one(
                {"pm_id": pm_id, "code": channel_code},
                {"$set": new_fields},
            )
            if channel_obj:
                print(f"  * Payment channel: {channel_name} updated")
            else:
                print(f"  ! Payment channel: {channel_name} not updated")


async def unregister_payment_methods():
    for pg, pm_data in UNUSED_PAYMENT_METHODS.items():
        pg_obj = await collections.payment_gateway.find_one({"name": pg})
        pg_id = str(pg_obj["_id"])
        for pm, channel_code in pm_data.items():
            pm_obj = await collections.payment_method.find_one(
                {"pg_id": pg_id, "code": pm.value}
            )
            if pm_obj:
                pm_id = str(pm_obj["_id"])
                print(f"  * Unregistering payment method: {pm.value} ({channel_code})")
                pc_filter = {"pm_id": pm_id, "code": channel_code}
                result: DeleteResult = await collections.payment_channel.delete_one(
                    pc_filter
                )
                msg = (
                    "   * Payment channel deleted"
                    if result.deleted_count > 0
                    else "   ! Payment channel already deleted"
                )
                print(msg)
