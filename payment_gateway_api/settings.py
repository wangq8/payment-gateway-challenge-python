from pydantic_settings import BaseSettings, SettingsConfigDict


class PaymentSettings(BaseSettings):
    bank_url: str = "http://localhost:8080"
    bank_timeout: int = 10
    # not implemented
    bank_retry: int = 3
    # not implemented
    bank_retry_delay: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


payment_settings = PaymentSettings()
