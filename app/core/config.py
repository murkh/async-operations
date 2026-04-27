from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "async_operations"
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
