from typing import Awaitable

from bson import ObjectId
from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError

from app import collections, settings
from app.core import fernet
from app.core.exceptions import TokenExpiredException
from app.core.models import User
from app.core.security import oauth2_scheme
from app.extensions import jwt

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def token_required(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> User:
    async def on_invalid():
        raise credentials_exception

    async def on_expired():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token has expired")

    user_obj = await _find_user(token, on_invalid, on_expired, jwt_required=False)
    request.state.user = user_obj
    return user_obj


async def jwt_required(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> User:
    async def on_invalid():
        raise credentials_exception

    async def on_expired():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token has expired")

    user_obj = await _find_user(token, on_invalid, on_expired, jwt_required=True)
    request.state.user = user_obj
    return user_obj


async def get_current_user_ws(
    ws: WebSocket,
) -> User:
    authorization: str = ws.headers.get("Authorization")
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != "bearer":
        print("Invalid request")
        await ws.close(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA)

    async def on_invalid():
        print("Invalid:", ws)
        await ws.close(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA)

    async def on_expired():
        print("Expired:", ws)
        await ws.close(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA)

    return await _find_user(token, on_invalid, on_expired, jwt_required=True)


async def _find_user(
    token: str,
    on_invalid: Awaitable,
    on_expired: Awaitable,
    *,
    jwt_required: bool = False
) -> User:
    try:
        payload = jwt.decode(token)
        user_id: str = payload.get("sub")
        if not user_id:
            await on_invalid()
            return
    except ExpiredSignatureError:
        await on_expired()
        return
    except JWTError:
        if jwt_required:
            await on_invalid()
            return

        api_key_obj = await collections.api_keys.find_one({"api_key": token})
        if api_key_obj:
            secret_key: str = api_key_obj["secret_key"]
            try:
                user_id = fernet.decrypt(token, secret_key)
                if not user_id:
                    await on_invalid()
                    return
            except TokenExpiredException:
                await on_expired()
                return
            except ValueError:
                await on_invalid()
                return
        else:
            await on_invalid()
            return

    user: dict = await collections.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        await on_invalid()
        return

    user["id"] = str(user.pop("_id"))
    user_obj = User(**user)
    return user_obj


async def validate_xendit_payment(request: Request):
    secret_key = request.headers.get("x-callback-token")
    if not secret_key:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid request")

    if secret_key != settings.XENDIT_SECRET_KEY:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid request")

    print("Xendit request valid")
