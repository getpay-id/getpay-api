from datetime import timedelta
from typing import Optional

from fastapi import Depends, Form, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app import collections, settings
from app.core import passwd
from app.extensions import jwt


class SignInForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(None, regex="password"),
        username: EmailStr = Form(..., description="Username (email)"),
        password: str = Form(..., min_length=8, description="Password"),
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


async def signin(form_data: SignInForm = Depends()):
    """
    Dapatkan akses token.

    Parameters:

    * `username`: Username (email)

    * `password`: Password

    """

    username = form_data.username
    password = form_data.password
    user_data: dict = await collections.users.find_one({"username": username})
    if not user_data:
        return ORJSONResponse(
            {"detail": "Invalid username or password"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    valid = passwd.verify(password, user_data["password"])
    if not valid:
        return ORJSONResponse(
            {"detail": "Invalid username or password"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    payload = {
        "sub": str(user_data["_id"]),
    }
    expire_time = timedelta(days=1) if settings.DEBUG else timedelta(minutes=20)
    access_token = jwt.create(payload, expire=expire_time)
    return ORJSONResponse(
        {
            "detail": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
        }
    )
