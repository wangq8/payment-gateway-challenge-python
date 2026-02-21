import uuid
from unittest.mock import Mock, AsyncMock, patch

import httpx
import pytest

from payment_gateway_api.clients import BankClient
from payment_gateway_api.models import BankPaymentRequest


class TestBankClient:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("authorized", [
        True,
        False,
    ])
    async def test_process_payment_positive(self, authorized):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"authorized": authorized, "authorization_code": uuid.uuid4()}

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_response

        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch('payment_gateway_api.settings.payment_settings.bank_url') as _, \
            patch('payment_gateway_api.settings.payment_settings.bank_timeout') as _, \
            patch('httpx.AsyncClient', return_value=mock_client):
            payment = BankPaymentRequest(card_number="00001234", expiry_date="12/2036",
                                         currency="GBP", amount=100, cvv="345")
            client = BankClient()
            response = await client.process_payment(payment)

            assert response is not None
            assert response.authorized is authorized
            assert response.authorization_code is not None
            assert mock_client.post.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code, expected_message", [
        (400, "Internal server error"),
        (500, "Downstream bank server is unavailable, please retry later."),
    ])
    async def test_process_payment_negative(self, code, expected_message):
        mock_response = Mock()
        mock_response.status_code = code

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_response

        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch('payment_gateway_api.settings.payment_settings.bank_url') as _, \
            patch('payment_gateway_api.settings.payment_settings.bank_timeout') as _, \
            patch('httpx.AsyncClient', return_value=mock_client), \
            pytest.raises(Exception) as ex_info:
            payment = BankPaymentRequest(card_number="00001234", expiry_date="12/2036",
                                         currency="GBP", amount=100, cvv="345")
            client = BankClient()
            await client.process_payment(payment)

            assert str(ex_info.value) == expected_message
            assert mock_client.post.call_count == 1

    @pytest.mark.asyncio
    async def test_process_payment_error(self):
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.side_effect = httpx.RequestError("Network error")  # diff

        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        with patch('payment_gateway_api.settings.payment_settings.bank_url') as _, \
            patch('payment_gateway_api.settings.payment_settings.bank_timeout') as _, \
            patch('httpx.AsyncClient', return_value=mock_client), \
            pytest.raises(Exception) as ex_info:
            payment = BankPaymentRequest(card_number="00001234", expiry_date="12/2036",
                                         currency="GBP", amount=100, cvv="345")
            client = BankClient()
            await client.process_payment(payment)

            assert str(ex_info.value) == "Request error: Network error"
            assert mock_client.post.call_count == 1
