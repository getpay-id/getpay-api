import pytest

from .core.client import client
from .core.marker import after_signin

wait_create_apikey = pytest.mark.order(after=["test_apikey.py::test_create_apikey"])


@after_signin
def test_create_apikey(auth_headers: dict, request: pytest.FixtureRequest):
    payload = {
        "name": "Mamang April",
        "description": "API Key khusus Mamang April",
        "expiration_time": 0,
        "expiration_type": "unlimited",
    }
    response = client.post("/apikey/", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    request.config.cache.set("apikey_object", data)


@wait_create_apikey
def test_get_all_apikey(auth_headers: dict, request: pytest.FixtureRequest):
    response = client.get("/apikey/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0


@wait_create_apikey
def test_get_detail_apikey(auth_headers: dict, request: pytest.FixtureRequest):
    apikey_object = request.config.cache.get("apikey_object", None)
    if not apikey_object:
        pytest.fail("No API Key found.")

    apikey_id = apikey_object["id"]
    response = client.get(f"/apikey/{apikey_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == apikey_id


@wait_create_apikey
def test_update_apikey(auth_headers: dict, request: pytest.FixtureRequest):
    apikey_object = request.config.cache.get("apikey_object", None)
    if not apikey_object:
        pytest.fail("No API Key found.")

    apikey_id = apikey_object["id"]
    ganti_nama_str = "ganti nama"
    ganti_deskripsi_str = "ganti deskripsi"
    payload = {
        "name": ganti_nama_str,
        "description": ganti_deskripsi_str,
    }
    response = client.put(f"/apikey/{apikey_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == ganti_nama_str and data["description"] == ganti_deskripsi_str


@wait_create_apikey
def test_delete_apikey(auth_headers: dict, request: pytest.FixtureRequest):
    apikey_object = request.config.cache.get("apikey_object", None)
    if not apikey_object:
        pytest.fail("No API Key found.")

    apikey_id = apikey_object["id"]
    response = client.delete(f"/apikey/{apikey_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
