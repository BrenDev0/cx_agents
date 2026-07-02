from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV: str = "local"
    ALLOW_ORIGINS: list[str] = ["http://localhost:8000"]
    
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_PORT: str

    OPENAI_API_KEY: str

    REDIS_URL: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )

    DATABASE_URL: str

    ENCRYPTION_KEY: str

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str | None = None
    AWS_BUCKET_NAME: str | None = None
    BUCKET_ENDPOINT: str | None = None

    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    REGISTRATION_MAX_ATTEMPS: int = 5
    LOGIN_MAX_ATTEMPS: int = 5

settings = Settings() # type: ignore[call-arg]