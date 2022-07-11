import random

import pytest

from app.core.enums import PaymentMethod, TransactionStatus

from .core.client import client
from .core.marker import wait_get_all_active_payment_method

wait_create_transaction = pytest.mark.order(
    after=["test_transaction.py::test_create_transaction"]
)


@wait_get_all_active_payment_method
def test_create_transaction(auth_headers: dict, request: pytest.FixtureRequest):
    payment_method_list = request.config.cache.get("payment_method", None)
    if not payment_method_list:
        pytest.fail("No payment method found")

    payment_method = random.choice(payment_method_list)
    payment_method_code = payment_method["code"]
    payment_channel = random.choice(payment_method["channels"])
    payment_channel_code = payment_channel["code"]
    payload = {
        "name": "Mamang April",
        "phone_number": "08912345678",
        "email": "mamang@aprila.dev",
        "amount": 15000,
        "payment_method": payment_method_code,
        "payment_channel": payment_channel_code,
    }
    if payment_method_code == PaymentMethod.ewallet:
        payload["ewallet_success_redirect_url"] = "https://aprila.dev"

    response = client.post("/transaction/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    request.config.cache.set("transaction_object", data)


@wait_create_transaction
def test_get_all_transaction(auth_headers: dict, request: pytest.FixtureRequest):
    response = client.get("/transaction/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0


@wait_create_transaction
def test_get_detail_transaction(request: pytest.FixtureRequest, auth_headers: dict):
    transaction_object = request.config.cache.get("transaction_object", None)
    if not transaction_object:
        pytest.fail("No transaction object found")

    transaction_id = transaction_object["id"]
    response = client.get(f"/transaction/{transaction_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    trx_id = data["id"]
    assert trx_id == transaction_id


@wait_create_transaction
def test_update_transaction(request: pytest.FixtureRequest, auth_headers: dict):
    transaction_object = request.config.cache.get("transaction_object", None)
    if not transaction_object:
        pytest.fail("No transaction object found")

    transaction_id = transaction_object["id"]
    payload = {
        "status": TransactionStatus.paid.value,
    }
    response = client.put(
        f"/transaction/{transaction_id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] and data["data"]["status"] != transaction_object["status"]
