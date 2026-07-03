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
    BUCKET_ENDPOINT: str 

    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    REGISTRATION_MAX_ATTEMPS: int = 5
    LOGIN_MAX_ATTEMPS: int = 5

    def _require(self, value: str | None, name: str) -> str:
        if not value:
            raise ValueError(f"{name} is not configured")

        return value

    def require_qdrant_url(self) -> str:
        return self._require(self.QDRANT_URL, "QDRANT_URL")

    def require_qdrant_collection_name(self) -> str:
        return self._require(self.QDRANT_COLLECTION_NAME, "QDRANT_COLLECTION_NAME")

    def require_smtp_host(self) -> str:
        return self._require(self.SMTP_HOST, "SMTP_HOST")

    def require_smtp_user(self) -> str:
        return self._require(self.SMTP_USER, "SMTP_USER")

    def require_smtp_password(self) -> str:
        return self._require(self.SMTP_PASSWORD, "SMTP_PASSWORD")

settings = Settings() # type: ignore[call-arg]