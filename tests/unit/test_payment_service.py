import uuid
from unittest.mock import patch, AsyncMock

import pytest

from payment_gateway_api.clients import BankClient
from payment_gateway_api.exceptions import PaymentNotFoundError, BankServerError
from payment_gateway_api.models import PaymentResponse, PaymentStatus, BankPaymentResponse, PaymentRequest
from payment_gateway_api.services import PaymentService


class TestPaymentService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("authorized, expected_status", [
        (True, PaymentStatus.AUTHORIZED),
        (False, PaymentStatus.DECLINED),
    ])
    async def test_process_payment_positive(self, authorized, expected_status):
        with patch('payment_gateway_api.repositories.repo.add') as mock_repo_add:
            mock_bank_client = AsyncMock(spec=BankClient)
            mock_bank_client.process_payment.return_value = BankPaymentResponse(
                authorized=authorized, authorization_code=uuid.uuid4())
            service = PaymentService(mock_bank_client)
            payment = PaymentRequest(card_number="00001234", expiry_month="12", expiry_year="2036",
                                     currency="GBP", amount=100, cvv="345")
            result = await service.process_payment(payment)
            assert result is not None
            assert result.id is not None
            assert result.status == expected_status
            assert result.card_last4 == "1234"
            assert result.expiry_month == "12"
            assert result.expiry_year == "2036"
            assert result.currency == "GBP"
            assert result.amount == 100
            assert mock_bank_client.process_payment.call_count == 1
            assert mock_repo_add.call_count == 1

    @pytest.mark.asyncio
    async def test_process_payment_negative(self):
        with patch('payment_gateway_api.repositories.repo.add') as mock_repo_add:
            mock_bank_client = AsyncMock(spec=BankClient)
            mock_bank_client.process_payment.side_effect = BankServerError("Downstream error")
            service = PaymentService(mock_bank_client)
            payment = PaymentRequest(card_number="00001234", expiry_month="12", expiry_year="2036",
                                     currency="GBP", amount=100, cvv="345")
            with pytest.raises(BankServerError) as ex_info:
                await service.process_payment(payment)
                assert mock_repo_add.call_count == 0
                assert str(ex_info.value) == "Downstream error"

    def test_get_payment_not_found(self):
        with patch('payment_gateway_api.repositories.repo.get') as mock_repo_get:
            mock_repo_get.return_value = None
            mock_bank_client = AsyncMock(spec=BankClient)
            service = PaymentService(mock_bank_client)
            with pytest.raises(PaymentNotFoundError) as ex_info:
                new_id = uuid.uuid4()
                service.get_payment(new_id)
                assert mock_repo_get.call_count == 1
                assert str(ex_info.value) == f"Payment with id {new_id} not found"

    def test_get_payment_found(self):
        with patch('payment_gateway_api.repositories.repo.get') as mock_repo_get:
            new_id = uuid.uuid4()
            payment = PaymentResponse(
                id=new_id,
                status=PaymentStatus.AUTHORIZED,
                card_last4="1234",
                expiry_month="12",
                expiry_year="2036",
                currency="GBP",
                amount=100)
            mock_repo_get.return_value = payment
            mock_bank_client = AsyncMock(spec=BankClient)
            service = PaymentService(mock_bank_client)
            result = service.get_payment(new_id)
            assert mock_repo_get.call_count == 1
            assert payment == result
