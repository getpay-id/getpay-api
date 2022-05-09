from datetime import datetime, timedelta
from typing import Tuple

from cryptography.fernet import Fernet

from app.core.exceptions import TokenExpiredException


def create(message: str, exp: timedelta = None) -> Tuple[str, str]:
    """Membuat token fernet.
    Args:
        message (str): data
        exp (timedelta, optional): waktu kadaluwarsa token
    Returns:
        Tuple[str, str]: kunci, token
    """
    key = Fernet.generate_key().decode()
    fernet = Fernet(key)
    if exp:
        seconds = (datetime.utcnow().replace(microsecond=0) + exp).timestamp()
        pw = fernet.encrypt_at_time(message.encode(), int(seconds)).decode()
    else:
        pw = fernet.encrypt(message.encode()).decode()
    return key, pw


def decrypt(token: str, key: str) -> str:
    """Decode fernet
    Args:
        token (str): token.
        key (str): kunci untuk membuka fernet
    Raises:
        TokenExpiredException: ketika token sudah kadaluwarsa.
    Returns:
        str: data
    """

    token = token.encode()
    fernet = Fernet(key.encode())
    timestamp = fernet.extract_timestamp(token)
    exp = datetime.fromtimestamp(timestamp)
    if exp and datetime.utcnow().replace(microsecond=0) > exp:
        raise TokenExpiredException("token has expired")

    data = fernet.decrypt(token).decode()
    return data
