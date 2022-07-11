import pytest

from .core.client import client
from .core.marker import after_signin


@after_signin
def test_get_all_active_payment_method(
    auth_headers: dict, request: pytest.FixtureRequest
):
    response = client.get("/payment/active", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data) > 0
    request.config.cache.set("payment_method", data)
