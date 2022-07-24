"""
Skrip ini untuk membuat transaksi menggunakan semua payment method yang aktif.
Ini bertujuan untuk mencari respon yang tidak sesuai dengan yang diharapkan.
"""

import dotenv

dotenv.load_dotenv(".env.testing")

import os

import requests

from app.core.enums import PaymentMethod

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

host = "http://localhost:5000/v1"
headers = {}


def init_access_token():
    global headers
    r = requests.post(
        f"{host}/auth/signin", data={"username": USER_EMAIL, "password": USER_PASSWORD}
    )
    data = r.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}


def http_request(method: str, path: str, data: dict = None) -> requests.Response:
    url = f"{host}{path}"
    r = requests.request(method, url, json=data, headers=headers)
    return r


def get_all_payment_methods():
    r = http_request("get", "/payment/active")
    data = r.json()
    return data


def test_payment():
    payment_method_list = get_all_payment_methods()
    for payment_method in payment_method_list:
        pm_code = payment_method["code"]
        for payment_channel in payment_method["channels"]:
            payload = {
                "name": "Mamang April",
                "phone_number": "08912345678",
                "email": "mamang@aprila.dev",
                "amount": 15000,
                "payment_method": pm_code,
                "payment_channel": payment_channel["code"],
            }
            if pm_code == PaymentMethod.ewallet:
                payload["ewallet_success_redirect_url"] = "https://aprila.dev"

            response = http_request("post", "/transaction/", payload)
            if response.status_code != 200:
                print(payload)
                print(response.text)
                print("=" * 80)


def main():
    init_access_token()
    test_payment()


if __name__ == "__main__":
    main()
