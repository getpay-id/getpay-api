import random

import pytest

from app.core.enums import PaymentStatus

from .core.client import client
from .core.marker import after_signin

wait_get_all = pytest.mark.order(
    after=["test_payment_gateway.py::test_get_all_payment_gateway"]
)


@after_signin
def test_get_all_payment_gateway(auth_headers: dict, request: pytest.FixtureRequest):
    response = client.get("/payment/gateway", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    total_data = len(data)
    assert total_data == 3
    pg_obj = random.choice(data)
    pg_id = pg_obj["id"]
    request.config.cache.set("pg_id", pg_id)


@wait_get_all
def test_update_payment_gateway(auth_headers: dict, request: pytest.FixtureRequest):
    pg_id = request.config.cache.get("pg_id", None)
    if not pg_id:
        pytest.fail("No payment gateway id found")

    def set_status(status: PaymentStatus):
        payload = {
            "status": status.value,
        }
        response = client.put(
            f"/payment/gateway/{pg_id}", json=payload, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status

    set_status(PaymentStatus.inactive)
    set_status(PaymentStatus.active)
