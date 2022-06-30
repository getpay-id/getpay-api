from functools import wraps
from typing import Callable, List, Tuple, TypeVar, Union

from typing_extensions import ParamSpec
from xendit import (
    QRCode,
    QRCodeType,
    RetailOutlet,
    VirtualAccount,
    VirtualAccountBank,
    Xendit,
)
from xendit.models.ewallet.ewallet_charge import EWalletCharge
from xendit.xendit_error import XenditError

PT = ParamSpec("PT")
RT = TypeVar("RT")


def handle_error(func: Callable[..., RT]) -> Callable[..., RT]:
    @wraps(func)
    def wrapped(*args: PT.args, **kwargs: PT.kwargs) -> RT:
        try:
            resp = func(*args, **kwargs)
            success = True
        except XenditError as e:
            resp = {"detail": " ".join(e.args), "data": e.errors}
            success = False

        return success, resp

    return wrapped


def get_xendit_client(api_key: str) -> Xendit:
    return Xendit(
        api_key=api_key,
    )


def get_virtual_account_banks(api_key: str) -> List[VirtualAccountBank]:
    x = get_xendit_client(api_key)
    return x.VirtualAccount.get_banks()


@handle_error
def create_virtual_account_payment(
    api_key: str,
    *,
    external_id: str,
    bank_code: str,
    name: str,
    expected_amount: int,
    expiration_date: str,
    **kwargs
) -> Tuple[bool, Union[VirtualAccount, dict]]:
    x = get_xendit_client(api_key)
    resp = x.VirtualAccount.create(
        external_id="va-" + external_id,
        bank_code=bank_code,
        name=name,
        expected_amount=expected_amount,
        expiration_date=expiration_date,
        **kwargs
    )
    return resp


@handle_error
def create_qris_payment(
    api_key: str,
    *,
    external_id: str,
    callback_url: str,
    amount: int,
    type: str = QRCodeType.DYNAMIC,
    **kwargs
) -> Tuple[bool, Union[dict, QRCode]]:
    x = get_xendit_client(api_key)
    resp = x.QRCode.create(
        external_id="qrcode-" + external_id,
        callback_url=callback_url,
        amount=amount,
        type=type,
        **kwargs
    )
    return resp


@handle_error
def create_retail_outlet_payment(
    api_key: str,
    *,
    external_id: str,
    retail_outlet_name: str,
    name: str,
    expected_amount: int,
    expiration_date: str,
    **kwargs
) -> Tuple[bool, Union[dict, RetailOutlet]]:
    x = get_xendit_client(api_key)
    resp = x.RetailOutlet.create_fixed_payment_code(
        external_id="cstore-" + external_id,
        retail_outlet_name=retail_outlet_name,
        name=name,
        expected_amount=expected_amount,
        expiration_date=expiration_date,
        **kwargs
    )
    return resp


@handle_error
def create_ewallet_payment(
    api_key: str,
    *,
    external_id: str,
    amount: int,
    channel_code: str,
    channel_properties: dict = {},
    **kwargs
) -> Tuple[bool, Union[dict, EWalletCharge]]:
    x = get_xendit_client(api_key)
    resp = x.EWallet.create_ewallet_charge(
        reference_id="ewallet-" + external_id,
        currency="IDR",
        amount=amount,
        checkout_method="ONE_TIME_PAYMENT",
        channel_code=channel_code,
        channel_properties=channel_properties,
        **kwargs
    )
    return resp
