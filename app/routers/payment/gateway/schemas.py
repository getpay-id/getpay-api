from app.core.enums import PaymentStatus
from app.core.schema import Schema


class PaymentGatewaySchema(Schema):
    name: str
    status: PaymentStatus
