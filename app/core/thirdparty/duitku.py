import datetime
import hashlib

import requests

from app.core.utils import generate_random_string

BASE_PATH = "/webapi/api/merchant"


def get_payment_methods(url: str, api_key: str, merchant_code: str):
    url = url.rstrip("/") + f"{BASE_PATH}/paymentmethod/getpaymentmethod"
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    amount = 1
    signature = hashlib.sha256(
        f"{merchant_code}{amount}{dt}{api_key}".encode()
    ).hexdigest()
    data = {
        "merchantcode": merchant_code,
        "amount": amount,
        "datetime": dt,
        "signature": signature,
    }
    resp: dict = requests.get(url, json=data).json()
    payments = resp.get("paymentFee", [])
    return payments


def request_transaction(
    url: str,
    api_key: str,
    merchant_code: str,
    *,
    name: str,
    email: str,
    phone_number: str,
    amount: int,
    paymentMethod: str,
    expiryPeriod: int = 60,
):
    url = url.rstrip("/") + f"{BASE_PATH}/v2/inquiry"
    trx_id = "gp-" + generate_random_string()
    signature = hashlib.md5(
        f"{merchant_code}{trx_id}{amount}{api_key}".encode()
    ).hexdigest()
    data = {
        "merchantCode": merchant_code,
        "paymentAmount": amount,
        "paymentMethod": paymentMethod,
        "merchantOrderId": trx_id,
        "customerVaName": name,
        "email": email,
        "phoneNumber": phone_number,
        "signature": signature,
        "expiryPeriod": expiryPeriod,
    }
    resp = requests.post(url, json=data)
    return trx_id, resp
