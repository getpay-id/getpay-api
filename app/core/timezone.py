from datetime import datetime


def now(utc: bool = True) -> datetime:
    func = datetime.utcnow if utc else datetime.now
    return func()
