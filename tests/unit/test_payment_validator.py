from datetime import datetime, timedelta

import pytest

from payment_gateway_api.exceptions import BusinessValidationError
from payment_gateway_api.models import PaymentRequest
from payment_gateway_api.validators import PaymentValidator


class TestPaymentValidator:
    @pytest.mark.parametrize("card_number,expiry_month,expiry_year,currency,amount,cvv,expected_message", [
        ('12345678901234', '1', '1999', 'GBP', 123, '1234', "expiry_year and expiry_month must be in the future."),
        ('abc', '1', '1999', 'GBP', -1, '1234',
         "card_number must be a 14-19 length numeric. expiry_year and expiry_month must be in the future. amount must be positive."),
        ('abc', '2', '2000', 'XYZ', 123, '1234',
         "card_number must be a 14-19 length numeric. expiry_year and expiry_month must be in the future. currency XYZ is not supported."),
        ('abc', '13', '999', 'YYY', 1, '12',
         "card_number must be a 14-19 length numeric. expiry_month must be 1-12. expiry_year must be a 4 length numeric. currency YYY is not supported. cvv must be a 3-4 length numeric."),
    ])
    def test_validate_payment_invalid(self, card_number, expiry_month, expiry_year, currency, amount, cvv, expected_message):
        payment = PaymentRequest(card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year,
                                 currency=currency, amount=amount, cvv=cvv)
        validator = PaymentValidator()
        with pytest.raises(BusinessValidationError) as ex_info:
            validator.validate_payment(payment)
            assert str(ex_info.value) == expected_message

    @pytest.mark.parametrize("card_number,expiry_month,expiry_year,currency,amount,cvv", [
        ('123456789012345', '1', '2036', 'GBP', 123, '1234'),
        ('1234567890123456', '12', '2046', 'USD', 789, '456'),
        ('12345678901234567', '10', '2056', 'CNY', 7890, '1456'),
    ])
    def test_validate_payment_valid(self, card_number, expiry_month, expiry_year, currency, amount, cvv):
        payment = PaymentRequest(card_number=card_number, expiry_month=expiry_month, expiry_year=expiry_year,
                                 currency=currency, amount=amount, cvv=cvv)
        validator = PaymentValidator()
        assert validator.validate_payment(payment) is None

    @pytest.mark.parametrize("card_number,expected_message", [
        (None, "card_number must be a 14-19 length numeric."),
        ("abc", "card_number must be a 14-19 length numeric."),
        ("1234567890123", "card_number must be a 14-19 length numeric."),
        ("12345678901234567890", "card_number must be a 14-19 length numeric."),
    ])
    def test_card_number_invalid(self, card_number, expected_message):
        validator = PaymentValidator()
        valid, message = validator._validate_card_number(card_number)
        assert not valid
        assert message == expected_message

    @pytest.mark.parametrize("card_number", [
        "12345678901234",
        "123456789012345",
        "1234567890123456",
        "12345678901234567",
        "123456789012345678",
        "1234567890123456789",
    ])
    def test_card_number_valid(self, card_number):
        validator = PaymentValidator()
        valid, message = validator._validate_card_number(card_number)
        assert valid
        assert message == ""

    @pytest.mark.parametrize("expiry_month,expiry_year,expected_message", [
        (None, "1234", "expiry_month must be 1-12."),
        ("01", "1234", "expiry_month must be 1-12."),
        ("13", "1234", "expiry_month must be 1-12."),
        ("12", None, "expiry_year must be a 4 length numeric."),
        ("12", "123", "expiry_year must be a 4 length numeric."),
        ("1", "2000", "expiry_year and expiry_month must be in the future."),
    ])
    def test_validate_expiry_date_invalid(self, expiry_month, expiry_year, expected_message):
        validator = PaymentValidator()
        valid, message = validator._validate_expiry_date(expiry_month, expiry_year)
        assert not valid
        assert message == expected_message

    @pytest.mark.parametrize("expiry_month,expiry_year", [
        ("9", "2036"),
        ("10", "2046"),
    ])
    def test_validate_expiry_date_valid(self, expiry_month, expiry_year):
        validator = PaymentValidator()
        valid, message = validator._validate_expiry_date(expiry_month, expiry_year)
        assert valid
        assert message == ""

    def test_validate_expiry_date_this_month(self):
        now = datetime.now()
        year = now.year
        month = now.month
        validator = PaymentValidator()
        valid, message = validator._validate_expiry_date(str(month), str(year))
        assert not valid
        assert message == "expiry_year and expiry_month must be in the future."

    def test_validate_expiry_date_next_month(self):
        now = datetime.now()
        future = now + timedelta(days=31)
        year = future.year
        month = future.month
        validator = PaymentValidator()
        valid, message = validator._validate_expiry_date(str(month), str(year))
        assert valid
        assert message == ""

    @pytest.mark.parametrize("currency,expected_message", [
        (None, "currency must be 3 upper case characters."),
        ("AB", "currency must be 3 upper case characters."),
        ("ABCD", "currency must be 3 upper case characters."),
        ("abc", "currency must be 3 upper case characters."),
        ("ZZZ", "currency ZZZ is not supported."),
    ])
    def test_validate_currency_invalid(self, currency, expected_message):
        validator = PaymentValidator()
        valid, message = validator._validate_currency(currency)
        assert not valid
        assert message == expected_message

    @pytest.mark.parametrize("currency", [
        "GBP",
        "USD",
        "CNY",
    ])
    def test_validate_currency_valid(self, currency):
        validator = PaymentValidator()
        valid, message = validator._validate_currency(currency)
        assert valid
        assert message == ""


    @pytest.mark.parametrize("amount,expected_message", [
        (-1, "amount must be positive."),
        (0, "amount must be positive."),
    ])
    def test_validate_amount_invalid(self, amount, expected_message):
        validator = PaymentValidator()
        valid, message = validator._validate_amount(amount)
        assert not valid
        assert message == expected_message

    @pytest.mark.parametrize("amount", [
        1,
        1050,
        999999999,
    ])
    def test_validate_amount_valid(self, amount):
        validator = PaymentValidator()
        valid, message = validator._validate_amount(amount)
        assert valid
        assert message == ""

    @pytest.mark.parametrize("cvv,expected_message", [
        (None, "cvv must be a 3-4 length numeric."),
        ("abc", "cvv must be a 3-4 length numeric."),
        ("12", "cvv must be a 3-4 length numeric."),
        ("12345", "cvv must be a 3-4 length numeric."),
    ])
    def test_validate_cvv_invalid(self, cvv, expected_message):
        validator = PaymentValidator()
        valid, message = validator._validate_cvv(cvv)
        assert not valid
        assert message == expected_message

    @pytest.mark.parametrize("cvv", [
        "123",
        "4567",
        "0000",
    ])
    def test_validate_cvv_valid(self, cvv):
        validator = PaymentValidator()
        valid, message = validator._validate_cvv(cvv)
        assert valid
        assert message == ""
