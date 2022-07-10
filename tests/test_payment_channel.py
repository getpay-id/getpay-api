import random

import pytest

from app.core.enums import PaymentStatus

from .lib.client import client
from .test_payment_method import wait_get_all as wait_get_all_payment_method

wait_get_all = pytest.mark.order(
    after=["test_payment_channel.py::test_get_all_payment_channel"]
)


@wait_get_all_payment_method
def test_get_all_payment_channel(auth_headers: dict, request: pytest.FixtureRequest):
    pm_id = request.config.cache.get("pm_id", None)
    if not pm_id:
        pytest.fail("No payment method id found")

    params = {"pm_id": pm_id}
    response = client.get("/payment/channel", params=params, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    total_data = len(data)
    assert total_data > 0
    pc_obj = random.choice(data)
    request.config.cache.set("pc_obj", pc_obj)


@wait_get_all
def test_get_detail_payment_channel(request: pytest.FixtureRequest, auth_headers: dict):
    pc_obj = request.config.cache.get("pc_obj", None)
    if not pc_obj:
        pytest.fail("No payment channel object found")

    pc_id = pc_obj["id"]
    response = client.get(f"/payment/channel/{pc_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pc_id


@wait_get_all
def test_update_payment_channel(request: pytest.FixtureRequest, auth_headers: dict):
    pc_obj: dict = request.config.cache.get("pc_obj", None)
    if not pc_obj:
        pytest.fail("No payment channel object found")

    pc_id = pc_obj["id"]

    def update(payload: dict, status: PaymentStatus):
        payload = payload.copy()
        payload["status"] = status.value
        response = client.put(
            f"/payment/channel/{pc_id}", json=payload, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status

    update(pc_obj, PaymentStatus.inactive)
    update(pc_obj, PaymentStatus.active)
