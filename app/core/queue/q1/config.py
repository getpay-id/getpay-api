from . import queue
from .tasks import update_transaction_status

Q1_SETTINGS = {
    "queue": queue,
    "functions": [update_transaction_status],
    "concurrency": 10,
}
