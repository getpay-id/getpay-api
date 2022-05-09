from typing import Optional

from pymongo.results import InsertOneResult

from app import collections, settings
from app.core import timezone
from app.core.constants import (
    CONVENIENCE_STORES,
    DUITKU_EWALLET,
    DUITKU_QRIS,
    DUITKU_RETAIL_OUTLET,
    DUITKU_VIRTUAL_ACCOUNTS,
    IPAYMU_VIRTUAL_ACCOUNTS,
    PAYMENT_METHODS,
    XENDIT_EWALLET,
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


async def create_payment_methods(
    pg_id: str, name: PaymentGateway, *, xendit_api_key: Optional[str] = None
):
    for pm_code in PaymentMethod:
        if name == PaymentGateway.ipaymu:
            if pm_code == PaymentMethod.ewallet:
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            if pm_code == PaymentMethod.va:
                for channel_code, channel_name in IPAYMU_VIRTUAL_ACCOUNTS.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.cstore:
                for (
                    channel_code,
                    channel_name,
                ) in CONVENIENCE_STORES.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.qris:
                channel_code = pm_code.value
                channel_name = "QRIS"
                await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.bank_transfer:
                channel_code = "bca"
                channel_name = IPAYMU_VIRTUAL_ACCOUNTS[channel_code]
                await create_payment_channel(pm_id, channel_name, channel_code)

        elif name == PaymentGateway.xendit:
            if pm_code == PaymentMethod.bank_transfer:
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            if pm_code == PaymentMethod.va:
                va_banks = xendit.get_virtual_account_banks(settings.XENDIT_API_KEY)
                for bank in va_banks:
                    channel_name = bank.name
                    channel_code = bank.code
                    status = (
                        PaymentStatus.active
                        if getattr(bank, "is_activated", False)
                        else PaymentStatus.inactive
                    )
                    await create_payment_channel(
                        pm_id, channel_name, channel_code, status
                    )

            elif pm_code == PaymentMethod.cstore:
                for (
                    channel_code,
                    channel_name,
                ) in CONVENIENCE_STORES.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.qris:
                channel_code = pm_code.value
                channel_name = "QRIS"
                await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.ewallet:
                for channel_code, channel_name in XENDIT_EWALLET.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

        elif name == PaymentGateway.duitku:
            if pm_code == PaymentMethod.bank_transfer:
                continue

            pm_id = await get_or_create_payment_method(pg_id, pm_code)
            if pm_code == PaymentMethod.va:
                for channel_code, channel_name in DUITKU_VIRTUAL_ACCOUNTS.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.cstore:
                for (
                    channel_code,
                    channel_name,
                ) in DUITKU_RETAIL_OUTLET.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.qris:
                for (
                    channel_code,
                    channel_name,
                ) in DUITKU_QRIS.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)

            elif pm_code == PaymentMethod.ewallet:
                for channel_code, channel_name in DUITKU_EWALLET.items():
                    await create_payment_channel(pm_id, channel_name, channel_code)


async def create_payment_channel(
    pm_id: str,
    channel_name: str,
    channel_code: str,
    status: PaymentStatus = PaymentStatus.active,
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
                "date_created": timezone.now(),
                "date_updated": None,
            }
        )
        print(f"  * Payment channel: {channel_name} created")
    else:
        print(f"  ! Payment channel: {channel_obj['name']} already exists")
