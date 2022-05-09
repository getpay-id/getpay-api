import re

from .enums import PaymentMethod

MONGO_COLLECTIONS = [
    "users",
    "api_keys",
    "payment_gateway",
    "payment_method",
    "payment_channel",
    "transactions",
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
