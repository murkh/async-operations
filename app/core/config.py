from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "async_operations"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    DEBUG: bool = False
    CACHE_TTL_SECONDS: int = 3600
    MAX_ACTIVE_JOBS_PER_USER: int = 3
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
