import uuid

from payment_gateway_api.clients import BankClient
from payment_gateway_api.exceptions import PaymentNotFoundError
from payment_gateway_api.mappers import map_to_bank_request, map_to_payment_response
from payment_gateway_api.models import PaymentRequest, PaymentResponse, PaymentStatus
from payment_gateway_api.repositories import repo


class PaymentService:
    def __init__(self, client: BankClient) -> None:
        self.client = client

    async def process_payment(self, payment: PaymentRequest) -> PaymentResponse:
        bank_response = await self.client.process_payment(map_to_bank_request(payment))
        status = PaymentStatus.AUTHORIZED if bank_response.authorized else PaymentStatus.DECLINED
        result = map_to_payment_response(uuid.uuid4(), status, payment)
        repo.add(result)
        return result

    def get_payment(self, payment_id: uuid.UUID) -> PaymentResponse:
        result = repo.get(payment_id)
        if result is None:
            raise PaymentNotFoundError(f'Payment with id {payment_id} not found')
        return result
