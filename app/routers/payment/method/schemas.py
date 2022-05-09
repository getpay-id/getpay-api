from app.core.schema import Schema


class PaymentMethod(Schema):
    code: str
    name: str
    status: int
