import logging

import httpx

from payment_gateway_api.exceptions import PaymentServerError, BankServerError
from payment_gateway_api.models import BankPaymentRequest, BankPaymentResponse
from payment_gateway_api.settings import payment_settings

logger = logging.getLogger(__name__)


class BankClient:
    def __init__(self):
        self._payments_url = f"{payment_settings.bank_url}/payments"
        self._timeout = payment_settings.bank_timeout

    async def process_payment(self, payment: BankPaymentRequest) -> BankPaymentResponse:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(self._payments_url, json=payment.model_dump())

                status = response.status_code
                if 400 <= status < 500:
                    # cannot retry - bad request - suppose not reach here, error message should not be exposed to caller.
                    logger.error("Client error %d : %s", status, response.text)
                    raise PaymentServerError("Internal server error")

                if 500 <= status < 600:
                    # possible retry for code 5XX
                    logger.error("Server error %d : %s", status, response.text)
                    raise BankServerError("Downstream bank server is unavailable, please retry later.")

                response_body = response.json()
                return BankPaymentResponse(**response_body)

            except httpx.RequestError as e:
                # might be network issue, e.g. wrong host/firewall issue, high load - server no response, etc.
                logger.error("Request Error: %s", str(e))
                raise PaymentServerError("Request error when calling downstream bank.")
