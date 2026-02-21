import logging
import re
from datetime import datetime

from payment_gateway_api.exceptions import BusinessValidationError
from payment_gateway_api.models import PaymentRequest

logger = logging.getLogger(__name__)

class PaymentValidator:
    CARD_NUMBER_REGEX = r'^[0-9]{14,19}$'
    EXPIRY_MONTH_REGEX = r'^([1-9]|1[0-2])$' # possible support 01 to add 0?
    EXPIRY_YEAR_REGEX = r'^[0-9]{4}$'
    CURRENCY_REGEX = r'^[A-Z]{3}$'
    CVV_REGEX = r'^[0-9]{3,4}$'
    SUPPORTED_CURRENCIES = {"GBP", "USD", "CNY"} # can be extracted to config file

    def validate_payment(self, payment: PaymentRequest) -> None:
        errors = []

        valid, message = self._validate_card_number(payment.card_number)
        if not valid:
            errors.append(message)

        valid, message = self._validate_expiry_date(payment.expiry_month, payment.expiry_year)
        if not valid:
            errors.append(message)

        valid, message = self._validate_currency(payment.currency)
        if not valid:
            errors.append(message)

        valid, message = self._validate_amount(payment.amount)
        if not valid:
            errors.append(message)

        valid, message = self._validate_cvv(payment.cvv)
        if not valid:
            errors.append(message)

        if len(errors) > 0:
            message = ' '.join(errors)
            logger.warning("Invalid payment information: %s", message)
            raise BusinessValidationError(message)

    def _validate_card_number(self, card_number: str) -> (bool, str):
        if not card_number or not re.match(PaymentValidator.CARD_NUMBER_REGEX, card_number):
            return False, 'card_number must be a 14-19 length numeric.'
        return True, ''

    def _validate_expiry_date(self, expiry_month, expiry_year) -> (bool, str):
        errors = []
        if not expiry_month or not re.match(PaymentValidator.EXPIRY_MONTH_REGEX, expiry_month):
            errors.append('expiry_month must be 1-12.')
        if not expiry_year or not re.match(PaymentValidator.EXPIRY_YEAR_REGEX, expiry_year):
            errors.append('expiry_year must be a 4 length numeric.')
        if len(errors) == 0:
            now = datetime.now()
            year = now.year
            month = now.month
            if year * 12 + month >= int(expiry_year) * 12 + int(expiry_month):
                errors.append('expiry_year and expiry_month must be in the future.')
        return len(errors) == 0, ' '.join(errors)

    def _validate_currency(self, currency: str) -> (bool, str):
        if not currency or not re.match(PaymentValidator.CURRENCY_REGEX, currency):
            return False, 'currency must be 3 upper case characters.'
        # possible to validate against ISO 4217
        if currency not in PaymentValidator.SUPPORTED_CURRENCIES:
            return False, f'currency {currency} is not supported.'
        return True, ''

    def _validate_amount(self, amount: int) -> (bool, str):
        if amount <= 0:
            return False, 'amount must be positive.'
        return True, ''

    def _validate_cvv(self, cvv: str) -> (bool, str):
        if not cvv or not re.match(PaymentValidator.CVV_REGEX, cvv):
            return False, 'cvv must be a 3-4 length numeric.'
        return True, ''
