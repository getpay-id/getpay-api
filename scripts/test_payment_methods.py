"""
Skrip ini untuk membuat transaksi menggunakan semua payment method yang aktif.
Ini bertujuan untuk mencari respon yang tidak sesuai dengan yang diharapkan.
"""

import dotenv

dotenv.load_dotenv(".env.testing")

import os
import sys

import qrcode
import requests

sys.path.insert(0, os.getcwd())

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
    phone_number = None
    payment_method_list = get_all_payment_methods()
    for payment_method in payment_method_list:
        pm_code = payment_method["code"]
        for payment_channel in payment_method["channels"]:
            min_amount = payment_channel["min_amount"] + 1
            payload = {
                "name": "Mamang April",
                "email": "mamang@aprila.dev",
                "amount": min_amount,
                "payment_method": pm_code,
                "payment_channel": payment_channel["code"],
            }
            if pm_code == PaymentMethod.ewallet:
                while not phone_number:
                    pn = input("Phone number: ")
                    if not pn or not pn.isdigit() or not pn.startswith("08"):
                        print("Invalid phone number")
                        continue

                    phone_number = pn

                payload["phone_number"] = phone_number
                payload["ewallet_success_redirect_url"] = "https://aprila.dev"

            response = http_request("post", "/transaction/", payload)
            if response.status_code == 200:
                data = response.json()
                print("Segera lakukan pembayaran sesuai dengan informasi di bawah ini:")
                if pm_code == PaymentMethod.va:
                    print("VA Number:", data["payment_number"])
                    print("Bank:", data["payment_channel"]["name"])
                elif pm_code == PaymentMethod.cstore:
                    print("Code:", data["payment_number"])
                    print("Convenience Store:", data["payment_channel"]["name"])
                elif pm_code == PaymentMethod.ewallet:
                    if payment_channel["name"].lower() == "ovo":
                        print("Klik 'Push Notifikasi' yang muncul di aplikasi OVO")
                    else:
                        print(
                            "Klik link dibawah ini untuk melakukan pembayaran (PILIH SALAH SATU):"
                        )
                        for link in data["payment_number"].values():
                            if link:
                                print("* " + link)

                elif pm_code == PaymentMethod.qris:
                    qr = qrcode.QRCode(box_size=4, border=1)
                    qr.add_data(data["payment_number"])
                    qr.print_ascii()
                    print("Segera scan QR code di atas untuk melakukan pembayaran")

                input(
                    "Jika sudah menyelesaikan pembayaran.\nTekan enter untuk melanjutkan..."
                )

            else:
                print("=" * 80)
                print(payload)
                print(response.text)
                print("=" * 80)


def main():
    try:
        init_access_token()
        test_payment()
    except KeyboardInterrupt:
        print("Aborted by user")


if __name__ == "__main__":
    main()
