import os

from saq import Queue

redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")
q1_db = os.environ.get("Q1_DB", "1")
queue = Queue.from_url(f"redis://{redis_host}:{redis_port}/{q1_db}")
