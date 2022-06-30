import hashlib
import hmac
import json

import requests

from app.core import timezone


def create_signature(data_body: str, va_account: str, api_key: str) -> str:
    encrypt_body = hashlib.sha256(data_body.encode()).hexdigest()
    stringtosign = "{}:{}:{}:{}".format("POST", va_account, encrypt_body, api_key)
    signature = (
        hmac.new(api_key.encode(), stringtosign.encode(), hashlib.sha256)
        .hexdigest()
        .lower()
    )
    return signature


def create_headers(signature: str, va_account: str) -> dict:
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    headers = {
        "Content-type": "application/json",
        "signature": signature,
        "va": va_account,
        "timestamp": timestamp,
    }
    return headers


def direct_payment(
    url: str,
    va_account: str,
    api_key: str,
    name: str,
    phone: str,
    email: str,
    amount: int,
    notifyUrl: str,
    expired: int,
    expiredType: str,
    paymentMethod: str,
    paymentChannel: str,
    product=None,
    qty=None,
    price=None,
    weight=None,
    width=None,
    height=None,
    length=None,
    deliveryArea=None,
    deliveryAddress=None,
    comments=None,
) -> dict:
    url = url.rstrip("/") + "/api/v2/payment/direct"
    body = {
        "name": name,
        "phone": phone,
        "email": email,
        "amount": amount,
        "notifyUrl": notifyUrl,
        "expired": expired,
        "expiredType": expiredType,
        "paymentMethod": paymentMethod,
        "paymentChannel": paymentChannel,
    }
    if comments:
        body["comments"] = comments

    if paymentMethod == "cod":
        body["product[]"] = product
        body["qty[]"] = qty
        body["price[]"] = price
        body["weight[]"] = weight
        body["width[]"] = width
        body["height[]"] = height
        body["length[]"] = length
        body["deliveryArea"] = deliveryArea
        body["deliveryAddress"] = deliveryAddress

    data_body = json.dumps(body, separators=(",", ":"))
    signature = create_signature(data_body, va_account, api_key)
    headers = create_headers(signature, va_account)
    resp = requests.post(url, data=data_body, headers=headers).json()
    return resp


def redirect_payment(
    url: str,
    va_account: str,
    api_key: str,
    product,
    qty,
    price,
    description,
    returnUrl,
    notifyUrl,
    cancelUrl,
    weight=None,
    dimension=None,
    buyerName=None,
    buyerPhone=None,
    buyerEmail=None,
    paymentMethod=None,
    pickupArea=None,
    pickupAddress=None,
) -> dict:
    url = url.rstrip("/") + "/api/v2/payment"
    body = {
        "product[]": product,
        "qty[]": qty,
        "price[]": price,
        "description[]": description,
        "returnUrl": returnUrl,
        "notifyUrl": notifyUrl,
        "cancelUrl": cancelUrl,
    }
    if weight:
        body["weight[]"] = weight
    if dimension:
        body["dimension[]"] = dimension
    if buyerName:
        body["buyerName"] = buyerName
    if buyerPhone:
        body["buyerPhone"] = buyerPhone
    if buyerEmail:
        body["buyerEmail"] = buyerEmail

    if paymentMethod == "cod":
        if pickupArea:
            body["pickupArea"] = pickupArea
        if pickupAddress:
            body["pickupAddress"] = pickupAddress

    data_body = json.dumps(body, separators=(",", ":"))
    signature = create_signature(data_body, va_account, api_key)
    headers = create_headers(signature, va_account)
    resp = requests.post(url, data=data_body, headers=headers).json()
    return resp
