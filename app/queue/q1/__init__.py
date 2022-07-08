import os

from saq import Queue

from app.core.utils import get_redis_url

q1_db = os.environ.get("Q1_DB", "1")
url = get_redis_url(db=q1_db)
queue = Queue.from_url(url)
