import os

import pytest

from .core.client import client

USER_EMAIL = os.environ.get("USER_EMAIL")
USER_PASSWORD = os.environ.get("USER_PASSWORD")


def test_signin(request: pytest.FixtureRequest):
    response = client.post(
        "/auth/signin", data={"username": USER_EMAIL, "password": USER_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in ["detail", "access_token", "token_type"])
    request.config.cache.set("jwt", data["access_token"])
