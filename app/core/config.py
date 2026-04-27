from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "async_operations"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    DEBUG: bool = False
    cache_ttl_seconds: int = 3600
    max_active_jobs_per_user: int = 3

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
