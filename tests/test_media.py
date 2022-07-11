import pytest

from .core.client import client
from .core.marker import after_signin

wait_upload_file = pytest.mark.order(after=["test_media.py::test_upload_file"])


@after_signin
def test_upload_file(request: pytest.FixtureRequest, auth_headers: dict):
    files = {"file": open("images/getpay-logo.png", "rb")}
    response = client.post("/media/", files=files, headers=auth_headers)
    assert response.status_code == 200
    request.config.cache.set("media_object", response.json())


@wait_upload_file
def test_get_all_media(auth_headers: dict):
    response = client.get("/media/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0


@wait_upload_file
def test_get_detail_media(request: pytest.FixtureRequest, auth_headers: dict):
    media_object = request.config.cache.get("media_object", None)
    if not media_object:
        pytest.fail("No media object found")

    media_id = media_object["id"]
    response = client.get(f"/media/{media_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    media_id = data["id"]
    assert media_id == media_id


@wait_upload_file
def test_update_media(request: pytest.FixtureRequest, auth_headers: dict):
    media_object = request.config.cache.get("media_object", None)
    if not media_object:
        pytest.fail("No media object found")

    files = {"file": open("images/payments/bca.png", "rb")}
    media_id = media_object["id"]
    response = client.post(f"/media/{media_id}", files=files, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["date_updated"]


@wait_upload_file
def test_delete_media(request: pytest.FixtureRequest, auth_headers: dict):
    media_object = request.config.cache.get("media_object", None)
    if not media_object:
        pytest.fail("No media object found")

    media_id = media_object["id"]
    response = client.delete(f"/media/{media_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
