from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from payment_gateway_api.app import app


@pytest.mark.parametrize("request_body, expected_message", [
    (None, "body: Field required"),
    ({},
     "card_number: Field required; expiry_month: Field required; expiry_year: Field required; currency: Field required; amount: Field required; cvv: Field required"),
    ({"card_number": "not-a-card",
      "expiry_month": "not-a-month",
      "expiry_year": "not-a-year",
      "currency": "not-a-currency",
      "amount": "not-an-integer",
      "cvv": "not-a-cvv"},
     "amount: Input should be a valid integer, unable to parse string as an integer"),
    ({"card_number": "not-a-card",
      "expiry_month": "not-a-month",
      "expiry_year": "not-a-year",
      "currency": "not-a-currency",
      "amount": -1,
      "cvv": "not-a-cvv"},
     "card_number must be a 14-19 length numeric. expiry_month must be 1-12. expiry_year must be a 4 length numeric. currency must be 3 upper case characters. amount must be positive. cvv must be a 3-4 length numeric."),
    ({"card_number": "12345678901234",
      "expiry_month": "12",
      "expiry_year": "2000",
      "currency": "AAA",
      "amount": 100,
      "cvv": "123"}, "expiry_year and expiry_month must be in the future. currency AAA is not supported.")
])
def test_validation_error(request_body, expected_message):
    client = TestClient(app)
    response = client.post("/api/v1/payments", json=request_body)
    assert response.status_code == 400
    assert response.json()["message"] == expected_message


@pytest.mark.parametrize("request_body, status", [
    ({"card_number": "12345678901111",
      "expiry_month": "12",
      "expiry_year": "2036",
      "currency": "GBP",
      "amount": 123,
      "cvv": "123"}, "AUTHORIZED"),
    ({"card_number": "12345678902222",
      "expiry_month": "12",
      "expiry_year": "2046",
      "currency": "CNY",
      "amount": 456,
      "cvv": "4567"}, "DECLINED")
])
def test_process_success(request_body, status):
    client = TestClient(app)
    response = client.post("/api/v1/payments", json=request_body)
    assert response.status_code == 201
    assert response.json()["status"] == status


@pytest.mark.parametrize("request_body, message", [
    ({"card_number": "123456789011110",
      "expiry_month": "12",
      "expiry_year": "2036",
      "currency": "USD",
      "amount": 789,
      "cvv": "7890"}, "Downstream bank server is unavailable, please retry later."),
])
def test_process_error(request_body, message):
    client = TestClient(app)
    response = client.post("/api/v1/payments", json=request_body)
    assert response.status_code == 503
    assert response.json()["message"] == message


@pytest.mark.parametrize("request_body, message", [
    ({"card_number": "123456789011111",
      "expiry_month": "12",
      "expiry_year": "2036",
      "currency": "USD",
      "amount": 7890,
      "cvv": "7890"}, "Request error when calling downstream bank."),
])
def test_process_no_downstream(request_body, message):
    with patch('payment_gateway_api.settings.payment_settings.bank_url') as bank_url:
        bank_url.return_value = "http://localhost:12345"  # no such downstream
        client = TestClient(app)
        response = client.post("/api/v1/payments", json=request_body)
        assert response.status_code == 500
        assert response.json()["message"] == message
