# Payment Gateway Service

This is the Python version of the Payment Gateway challenge.

## Design
The application exposes two REST API endpoints: `POST /payments` and `GET /payments/{payment_id}`.
Incoming requests are first validated by the `PaymentValidator`, then they are processed by the `PaymentService`.
Within the service layer, it transforms the internal payment request into the bank specific payload format and sends it to the external bank server via `BankClient`.
Based on the bank’s response, the payment is marked as either AUTHORIZED or DECLINED and stored in memory for subsequent retrieval.
The API design document is: [payment_gateway_api.yaml](./payment_gateway_api.yaml).


## Key design considerations and assumptions
* Framework: Use FastAPI async IO for better performance.
* Framework: Use MVC
* API side: Add /api/v1 and prefix for the API versioning.
* API side: 201 for creation, 400 for Bad request, 500 for server error.
* API: Used enum for the currency and status, for caller and developer easy to use - [payment_gateway_api.yaml](./payment_gateway_api.yaml)
* MVC: separate a BankClient class for communicate with BankServer, for better structure.
* MVC: for the validator, return all the validation errors in one response instead of return error one by one, it is easier for the caller to adjust the input one time.
* MVC: use mapper to map the caller request to the bank request
* Security: DO NOT log the sensitive information such as card_number, cvv
* Security: DO NOT expose the response from bank server directly to the caller - need to hide the back end details.
* Configure: As requirement said allow 3 currencies, used an in memory set to allow 3 allowed currencies, they can be externalized to a config file latter when needed.
* Configure: Externalize the Bank server base URL to .env file to be configurable, easy to switch between dev, test, and production.
* Test: With UT and integration test to ensure quality.
* For the payment id, used an uuid since uuid is a random 128 bit ID, it is well format, impossible for collision, and widely used in industry as unique id for resources
* Supposes already handle all 400 Bad Request error from Bank server, if still meet 400 Bad request from bank server, might be the "payment gateway" issue, should return 500 Internal Error.


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
