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

settings = Settings() # type: ignore[call-arg]