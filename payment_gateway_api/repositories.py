import uuid

from payment_gateway_api.models import PaymentResponse


class PaymentRepository:
    def __init__(self):
        self._data = dict[uuid.UUID, PaymentResponse]()

    def add(self, payment: PaymentResponse) -> None:
        self._data[payment.id] = payment

    def get(self, payment_id: uuid.UUID) -> PaymentResponse:
        return self._data.get(payment_id, None)


repo = PaymentRepository()
