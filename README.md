# Payment Gateway Service

This is the Python version of the Payment Gateway challenge.

## Design
The application exposes two REST API endpoints: `POST /payments` and `GET /payments/{payment_id}`.
Incoming requests are first validated by the `PaymentValidator`, then they are processed by the `PaymentService`.
Within the service layer, it transforms the internal payment request into the bank specific payload format and sends it to the external bank server via `BankClient`.
Based on the bank’s response, the payment is marked as either AUTHORIZED or DECLINED and stored in memory for subsequent retrieval.
The API design document is: [payment_gateway_api.yaml](./payment_gateway_api.yaml).


## Key design considerations and assumptions
* Use MVC, with app (controller), validator, service, model.
* Use a dedicated `BankClient` to communicate with the external BankServer.
* Use `FastAPI` coroutine (async, await) to improve performance.
* Add `/api/v1` as prefix to for version.
* `POST /payments` return 400 Bad Request if request is invalid.
* `POST /payments` return all fields validation errors in one message.
* `POST /payments` to return 201 Created if success instead of 200 Ok.
* `GET /payments/{payment_id}` define `payment_id` to be UUID, avoid potential wrong format id.
* If bank server return `4XX error`, return `500 Internal server error` to caller since it is not the client side issue, but the payment gateway server issue.
* **DO NOT** expose the bank server response directly to caller.
* **DO NOT** log sensitive information such as `card_number`, `cvv`.
* To keep things simple, use an in memory set to allow only three currencies.
* Externalize `Bank server URL` to `.env` to be configurable, easy to switch between dev,test,production.
* Use enum for both `currency` and `status` in [payment_gateway_api.yaml](./payment_gateway_api.yaml) for caller easy to consume.
* With unit test and integration test to ensure quality.

## Possible enhance points
* Supported currencies can be externalized to config file.
* Add configurable retry when downstream server is unavailable (e.g. 503)
* Expose log level to be configurable.
* Possible abstract BankServer to support more banks.

## How to use

### Start
```commandline
poetry run python main.py
```

## File structure
```
├── app.py - expose the REST API POST /payments and GET /payments/{payment_id}.
├── validators.py - validate the payment request payload.
├── services.py - the business, call the bank client and store payment result.
├── clients.py - the client that inteact with downstream Bank Payment REST API.
├── tests/unit - the unit tests.
└── tests/integration - the integration tests.
```

### Unit Test
```commandline
poetry run pytest tests/unit
```

result similar as:
```
tests\unit\test_bank_client.py .....                                     [  8%]
tests\unit\test_payment_service.py .....                                 [ 17%]
tests\unit\test_payment_validator.py ................................... [ 78%]
............                                                             [100%]
============================= 57 passed in 0.44s ==============================
```

### Integration Test
```commandline
poetry run pytest tests/integration
```

result similar as:
```
tests\integration\test_app.py .........                                  [100%]
============================== 9 passed in 2.66s ==============================
```
