import uuid

from payment_gateway_api.models import PaymentRequest, BankPaymentRequest, PaymentStatus, PaymentResponse


def map_to_bank_request(payment: PaymentRequest) -> BankPaymentRequest:
    return BankPaymentRequest(
        card_number=payment.card_number,
        expiry_date=f"{payment.expiry_month}/{payment.expiry_year}",
        currency=payment.currency,
        amount=payment.amount,
        cvv=payment.cvv
    )


def map_to_payment_response(id: uuid.UUID, status: PaymentStatus, payment: PaymentRequest) -> PaymentResponse:
    return PaymentResponse(
        id=id,
        status=status,
        card_last4=payment.card_number[-4:],
        expiry_month=payment.expiry_month,
        expiry_year=payment.expiry_year,
        currency=payment.currency,
        amount=payment.amount
    )
