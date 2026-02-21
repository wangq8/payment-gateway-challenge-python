import logging

import uvicorn

# can be externalized as config file
LOG_LEVEL = "DEBUG"

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    uvicorn.run(
        app="payment_gateway_api.app:app",
        host='0.0.0.0',
        port=8000,
        reload=True,
        workers=1,
    )


if __name__ == "__main__":
    main()
