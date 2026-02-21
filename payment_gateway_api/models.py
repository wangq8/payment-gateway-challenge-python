import uuid
from enum import Enum

from pydantic import BaseModel, field_serializer, field_validator


class PaymentRequest(BaseModel):
    card_number: str
    expiry_month: str
    expiry_year: str
    currency: str
    amount: int
    cvv: str


class PaymentResponse(BaseModel):
    id: uuid.UUID
    status: PaymentStatus
    card_last4: str
    expiry_month: str
    expiry_year: str
    currency: str
    amount: int

    @field_serializer('status')
    def serialize_status(self, status: PaymentStatus):
        return status.name


class PaymentStatus(Enum):
    AUTHORIZED = 1
    DECLINED = 2


class BankPaymentRequest(BaseModel):
    card_number: str
    expiry_date: str
    currency: str
    amount: int
    cvv: str


class BankPaymentResponse(BaseModel):
    authorized: bool
    authorization_code: uuid.UUID | None

    # transfer the empty string to None
    @field_validator("authorization_code", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return None if v == "" else v


class ErrorResponse(BaseModel):
    message: str
