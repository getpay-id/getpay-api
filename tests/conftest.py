import warnings

import pytest


@pytest.fixture
def auth_headers(request: pytest.FixtureRequest):
    token = request.config.cache.get("jwt", None)
    if not token:
        warnings.warn("No JWT found.")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def apikey_headers(request: pytest.FixtureRequest):
    apikey_object = request.config.cache.get("apikey_object", None)
    if not apikey_object:
        warnings.warn("No API Key found.")

    return {"Authorization": f"Bearer {apikey_object['api_key']}"}
