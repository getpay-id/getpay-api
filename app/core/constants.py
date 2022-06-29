import re
from pathlib import Path

from .enums import PaymentGateway, PaymentMethod

BASE_PATH = Path(__file__).parent.parent.parent
PAYMENT_IMAGES_PATH = BASE_PATH / "images" / "payments"
STATIC_ROOT = "static"
STATIC_PAYMENT_IMAGES_PATH = BASE_PATH / STATIC_ROOT / "payments"
MONGO_COLLECTIONS = [
    "users",
    "api_keys",
    "payment_gateway",
    "payment_method",
    "payment_channel",
    "transactions",
    "media",
]

MONGO_TEXT_INDEXES = {
    "api_keys": ["name", "description"],
    "transactions": ["name", "email", "phone_number"],
}

PAYMENT_METHODS = {
    PaymentMethod.va: "Virtual Account",
    PaymentMethod.cstore: "Convenience Store",
    PaymentMethod.qris: "QRIS",
    PaymentMethod.bank_transfer: "Bank Transfer",
    PaymentMethod.ewallet: "Electronic Wallet",
}
IPAYMU_VIRTUAL_ACCOUNTS = {
    "cimb": "Bank CIMB Niaga",
    "bni": "Bank Negara Indonesia",
    "bag": "Bank Artha Graha",
    "mandiri": "Bank Mandiri",
    "bca": "Bank Central Asia",
    "bri": "Bank Rakyat Indonesia",
    "muamalat": "Bank Muamalat",
}
CONVENIENCE_STORES = {
    "indomaret": "Indomaret",
    "alfamart": "Alfamart",
}
IPAYMU_CONVENIENCE_STORES = CONVENIENCE_STORES.copy()
IPAYMU_QRIS = {
    "qris": "QRIS",
}
IPAYMU_BANK_TRANSFER = {
    "bca": "Bank Central Asia",
}
XENDIT_QRIS = IPAYMU_QRIS.copy()
XENDIT_CONVENIENCE_STORES = CONVENIENCE_STORES.copy()
XENDIT_EWALLET = {
    "id_ovo": "OVO",
    "id_dana": "DANA",
    "id_linkaja": "Link Aja",
    "id_shopeepay": "Shopee Pay",
    "id_sakuku": "Saku Ku",
}
PAYMENT_CHANNELS_DESCRIPTION = {
    **IPAYMU_VIRTUAL_ACCOUNTS,
    **CONVENIENCE_STORES,
    **XENDIT_EWALLET,
}

REDIS_PREFIX_TRANSACTION_CHANNEL = "transaction_"

ALPHA_NUMERIC_RE = re.compile(r"^[a-zA-Z0-9 ]+$")

DUITKU_VIRTUAL_ACCOUNTS = {
    # "BC": "Bank Central Asia", # payment not available
    "M2": "Bank Mandiri",
    "VA": "Maybank",
    "I1": "Bank Negara Indonesia",
    "B1": "Bank CIMB Niaga",
    "BT": "Permata Bank",
    "A1": "ATM Bersama",
    "AG": "Bank Artha Graha",
    "NC": "Bank Neo Commerce",
    "BR": "BRIVA",
    "S1": "Bank Sahabat Sampoerna",
}
DUITKU_RETAIL_OUTLET = {
    "FT": "Pegadaian / Alfamart / Pos",
    # "A2": "POS Indonesia", # payment not available
    "IR": "Indomaret",
}
DUITKU_EWALLET = {
    "OV": "OVO (Support Void)",
    "SA": "Shopee Pay (Support Void)",
    # "LF": "Link Aja (Fixed Fee)",
    # "LA": "Link Aja (Percentage Fee)",
    # "DA": "DANA"
}
DUITKU_QRIS = {
    "SP": "Shopee Pay",
    # "LQ": "Link Aja",
    # "NQ": "Nobu",
}

MIN_AMOUNT_PAYMENT_METHODS = {
    PaymentGateway.ipaymu: {
        # reference: https://documenter.getpostman.com/view/7508947/SWLfanD1?version=latest#79e948f6-66b0-4d45-be63-6320f020c834
        PaymentMethod.va: {pc: 10000 for pc in IPAYMU_VIRTUAL_ACCOUNTS.keys()},
        PaymentMethod.cstore: {pc: 10000 for pc in IPAYMU_CONVENIENCE_STORES.keys()},
        PaymentMethod.qris: {pc: 10000 for pc in IPAYMU_QRIS.keys()},
        PaymentMethod.bank_transfer: {pc: 10000 for pc in IPAYMU_BANK_TRANSFER.keys()},
    },
    PaymentGateway.xendit: {
        PaymentMethod.va: {
            # reference: https://developers.xendit.co/api-reference/#create-virtual-account
            **{
                pc: 1
                for pc in [
                    "MANDIRI",
                    "BNI",
                    "BJB",
                    "BRI",
                    "BSI",
                    "SAHABAT_SAMPOERNA",
                    "PERMATA",
                ]
            },
            "BCA": 10000,
        },
        PaymentMethod.cstore: {
            # reference: https://developers.xendit.co/api-reference/#create-fixed-payment-code
            pc: 10000
            for pc in XENDIT_CONVENIENCE_STORES.keys()
        },
        PaymentMethod.qris: {
            # reference: https://developers.xendit.co/api-reference/#create-qr-code
            pc: 1500
            for pc in XENDIT_QRIS.keys()
        },
        PaymentMethod.ewallet: {
            # reference: https://developers.xendit.co/api-reference/#create-ewallet-charge
            pc: 100
            for pc in XENDIT_EWALLET.keys()
        },
    },
    PaymentGateway.duitku: {
        # reference: https://docs.duitku.com/api/id/#metode-pembayaran
        PaymentMethod.va: {pc: 10000 for pc in DUITKU_VIRTUAL_ACCOUNTS.keys()},
        PaymentMethod.cstore: {pc: 10000 for pc in DUITKU_RETAIL_OUTLET.keys()},
        PaymentMethod.qris: {pc: 10000 for pc in DUITKU_QRIS.keys()},
        PaymentMethod.ewallet: {pc: 10000 for pc in DUITKU_EWALLET.keys()},
    },
}
