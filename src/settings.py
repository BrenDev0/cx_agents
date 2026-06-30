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

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str
    AWS_BUCKET_NAME: str

    REGISTRATION_MAX_ATTEMPS: int = 5
    LOGIN_MAX_ATTEMPS: int = 5

settings = Settings() # type: ignore[call-arg]