from pydantic import BaseModel


class SuccessLogin(BaseModel):
    detail: str
    access_token: str
    token_type: str
