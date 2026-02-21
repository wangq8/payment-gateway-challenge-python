import logging
import uuid

from fastapi import FastAPI, Request, Depends
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from payment_gateway_api.clients import BankClient
from payment_gateway_api.exceptions import BusinessValidationError, PaymentNotFoundError, PaymentServerError, \
    BankServerError
from payment_gateway_api.models import PaymentRequest, PaymentResponse, ErrorResponse
from payment_gateway_api.services import PaymentService
from payment_gateway_api.validators import PaymentValidator

logger = logging.getLogger(__name__)
app = FastAPI()


def get_bank_client() -> BankClient:
    return BankClient()


def get_payment_service(client: BankClient = Depends(get_bank_client)) -> PaymentService:
    return PaymentService(client)


def get_validator() -> PaymentValidator:
    return PaymentValidator()


@app.exception_handler(RequestValidationError)
async def basic_validation_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for error in errors:
        field = error['loc'][-1]
        msg = error['msg']
        error_messages.append(f"{field}: {msg}")
    merged_message = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(message=merged_message).model_dump()
    )


@app.exception_handler(BusinessValidationError)
async def business_validation_handler(request: Request, ex: BusinessValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(message=str(ex)).model_dump()
    )


@app.exception_handler(PaymentNotFoundError)
async def not_found_handler(request: Request, ex: PaymentNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(message=str(ex)).model_dump()
    )


@app.exception_handler(PaymentServerError)
async def business_validation_handler(request: Request, ex: PaymentServerError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(message=str(ex)).model_dump()
    )


@app.exception_handler(BankServerError)
async def business_validation_handler(request: Request, ex: BankServerError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(message=str(ex)).model_dump()
    )


@app.post("/api/v1/payments", status_code=status.HTTP_201_CREATED)
async def process_payment(
    request: PaymentRequest,
    validator: PaymentValidator = Depends(get_validator),
    service: PaymentService = Depends(get_payment_service)
) -> PaymentResponse:
    logger.debug("received a %s payment request", request.currency)
    validator.validate_payment(request)
    response = await service.process_payment(request)
    return response


@app.get("/api/v1/payments/{payment_id}")
async def get_payment(
    payment_id: uuid.UUID,
    service: PaymentService = Depends(get_payment_service)
) -> PaymentResponse:
    logger.debug("retrieve a payment with id %s", payment_id)
    return service.get_payment(payment_id)
