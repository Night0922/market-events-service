from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Market Events Service"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/market_events"
    redis_url: str = "redis://redis:6379/0"

    provider_a_api_key: str = "test-key"
    provider_b_api_key: str = "test-key"

    sync_ttl_seconds: int = 3600
    cache_ttl_seconds: int = 120
    provider_days_ahead: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
