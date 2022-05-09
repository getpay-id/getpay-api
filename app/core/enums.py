from enum import Enum, IntEnum

from pymongo import ASCENDING, DESCENDING


class WebSocketMediaType(str, Enum):
    dictionary = "dictionary"
    array = "array"


class UserRole(str, Enum):
    admin = "admin"
    member = "member"


class PaymentStatus(IntEnum):
    inactive = 0
    active = 1


class PaymentGateway(str, Enum):
    ipaymu = "ipaymu"
    xendit = "xendit"
    duitku = "duitku"


class PaymentMethod(str, Enum):
    va = "va"
    qris = "qris"
    cstore = "cstore"
    ewallet = "ewallet"
    bank_transfer = "bank_transfer"


class TransactionStatus(IntEnum):
    pending = 0
    paid = 1
    expired = 2


class SortBy(IntEnum):
    asc = ASCENDING
    desc = DESCENDING


class ExpirationType(str, Enum):
    unlimited = "unlimited"
    minutes = "minutes"
    hours = "hours"
    months = "months"
    years = "years"
