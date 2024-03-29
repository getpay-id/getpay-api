import os

from app.tasks import forward_callback, update_transaction_status

if "ENVFILE_LOADED" not in os.environ:
    from dotenv import load_dotenv

    load_dotenv(".env")
    os.environ["ENVFILE_LOADED"] = "1"

from urllib.parse import quote_plus

API_VERSION = os.environ.get("API_VERSION", "v1")
DEBUG = os.environ.get("DEBUG", "1") == "1"
MAX_UPLOAD_SIZE = 7000000  # 7MB
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set")
if len(JWT_SECRET_KEY) < 30:
    raise RuntimeError("JWT_SECRET_KEY is too short (30 chars minimum)")

NOTIFICATION_URL = os.environ.get("NOTIFICATION_URL")

# Sentry
SENTRY_DSN = os.environ.get("SENTRY_DSN")

# MongoDB
MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")
MONGODB_HOST = os.environ.get("MONGODB_HOST")
MONGODB_PORT = os.environ.get("MONGODB_PORT")
MONGODB_URL = os.environ.get(
    "MONGODB_URL",
    f"mongodb://{quote_plus(MONGODB_USERNAME)}:{quote_plus(MONGODB_PASSWORD)}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}",
)
if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not set")

# Redis
REDIS_USERNAME = os.environ.get("REDIS_USERNAME", "")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_DATABASE = os.environ.get("REDIS_DATABASE") or 0
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

# popol cache
CACHES = {
    "default": {
        "backend": "app.extensions.cache_backend.RedisCache",
        "options": {
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "db": REDIS_DATABASE,
        },
    },
}

# popol SAQ queue
Q1_DB = os.environ.get("Q1_DB", "1")
SAQ_QUEUES = {
    "default": {
        "url": f"redis://{REDIS_HOST}:{REDIS_PORT}/{Q1_DB}",
        "functions": [update_transaction_status, forward_callback],
        "concurrency": 10,
        "cron_jobs": [],
        "context": {},
    }
}

# IPaymu
IPAYMU_URL = os.environ.get("IPAYMU_URL")
IPAYMU_VIRTUAL_ACCOUNT = os.environ.get("IPAYMU_VIRTUAL_ACCOUNT")
IPAYMU_API_KEY = os.environ.get("IPAYMU_API_KEY")
IPAYMU_CALLBACK_URL = os.environ.get("IPAYMU_CALLBACK_URL")

# Xendit
XENDIT_API_KEY = os.environ.get("XENDIT_API_KEY")
XENDIT_SECRET_KEY = os.environ.get("XENDIT_SECRET_KEY")
XENDIT_QRCODE_CALLBACK_URL = os.environ.get("XENDIT_QRCODE_CALLBACK_URL")

# Duitku
DUITKU_URL = os.environ.get("DUITKU_URL")
DUITKU_API_KEY = os.environ.get("DUITKU_API_KEY")
DUITKU_MERCHANT_CODE = os.environ.get("DUITKU_MERCHANT_CODE")
