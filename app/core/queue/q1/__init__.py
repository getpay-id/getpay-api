import os

from saq import Queue

redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
redis_user = os.environ.get("REDIS_USERNAME")
redis_password = os.environ.get("REDIS_PASSWORD")
redis_auth = ""
if redis_user:
    redis_auth += f"{redis_user}:"

if redis_password:
    redis_auth = redis_auth.rstrip(":") + ":" + redis_password + "@"

q1_db = os.environ.get("Q1_DB", "1")
queue = Queue.from_url(f"redis://{redis_auth}{redis_host}:{redis_port}/{q1_db}")
