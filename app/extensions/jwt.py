from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app import settings


def create(
    data: dict,
    *,
    expire: Optional[timedelta] = None,
    key: str = settings.JWT_SECRET_KEY,
    algorithm: str = "HS256"
) -> str:
    """
    Create JSON web

    Args:
        data (dict): Payload to include in jwt.
        expire (Optional[timedelta]): Expiration time.
        key (str, optional): JWT secret key. Defaults to settings.JWT_SECRET_KEY.
        algorithm (str, optional): JWT Algorithm. Defaults to 'HS256'.

    Returns:
        str: Token.
    """

    data = data.copy()
    if expire:
        data["exp"] = datetime.utcnow() + expire

    return jwt.encode(data, key, algorithm=algorithm)


def decode(
    token: str, *, key: str = settings.JWT_SECRET_KEY, algorithm: str = "HS256"
) -> dict:
    """
    Decode JSON web

    Args:
        token (str): Token to decode.
        key (str, optional): JWT secret key. Defaults to settings.JWT_SECRET_KEY.
        algorithm (str, optional): JWT Algorithm. Defaults to 'HS256'.

    Returns:
        dict: Payload.
    """

    return jwt.decode(token, key, algorithms=[algorithm])
