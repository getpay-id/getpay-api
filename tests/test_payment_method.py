import random

import pytest

from app.core.enums import PaymentStatus

from .lib.client import client
from .test_payment_gateway import wait_get_all as wait_get_all_payment_gateway

wait_get_all = pytest.mark.order(
    after=["test_payment_method.py::test_get_all_payment_method"]
)


@wait_get_all_payment_gateway
def test_get_all_payment_method(request: pytest.FixtureRequest, auth_headers: dict):
    pg_id = request.config.cache.get("pg_id", None)
    if not pg_id:
        pytest.fail("No payment gateway id found")

    params = {"pg_id": pg_id}
    response = client.get("/payment/method", params=params, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    total_data = len(data)
    assert total_data > 0
    pm_obj = random.choice(data)
    pm_id = pm_obj["id"]
    request.config.cache.set("pm_id", pm_id)
    print("pm_id nih:", pm_id)


@wait_get_all
def test_get_detail_payment_method(request: pytest.FixtureRequest, auth_headers: dict):
    pm_id = request.config.cache.get("pm_id", None)
    if not pm_id:
        pytest.fail("No payment method id found")

    response = client.get(f"/payment/method/{pm_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pm_id


@wait_get_all
def test_update_payment_method(request: pytest.FixtureRequest, auth_headers: dict):
    pm_id = request.config.cache.get("pm_id", None)
    if not pm_id:
        pytest.fail("No payment method id found")

    def set_status(status: PaymentStatus):
        payload = {
            "status": status.value,
        }
        response = client.put(
            f"/payment/method/{pm_id}", json=payload, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status

    set_status(PaymentStatus.inactive)
    set_status(PaymentStatus.active)
