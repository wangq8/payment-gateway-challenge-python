class BusinessValidationError(Exception):
    pass


class PaymentNotFoundError(Exception):
    pass


class PaymentServerError(Exception):
    pass


class BankServerError(Exception):
    pass
