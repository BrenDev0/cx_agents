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

    def _require(self, value: str | None, name: str) -> str:
        if not value:
            raise ValueError(f"{name} is not configured")

        return value

    def require_aws_bucket_name(self) -> str:
        return self._require(self.AWS_BUCKET_NAME, "AWS_BUCKET_NAME")

    def require_aws_access_key_id(self) -> str:
        return self._require(self.AWS_ACCESS_KEY_ID, "AWS_ACCESS_KEY_ID")

    def require_aws_secret_access_key(self) -> str:
        return self._require(self.AWS_SECRET_ACCESS_KEY, "AWS_SECRET_ACCESS_KEY")

    def require_aws_region_name(self) -> str:
        return self._require(self.AWS_REGION_NAME, "AWS_REGION_NAME")

    def require_bucket_endpoint(self) -> str:
        return self._require(self.BUCKET_ENDPOINT, "BUCKET_ENDPOINT")

    def require_smtp_host(self) -> str:
        return self._require(self.SMTP_HOST, "SMTP_HOST")

    def require_smtp_user(self) -> str:
        return self._require(self.SMTP_USER, "SMTP_USER")

    def require_smtp_password(self) -> str:
        return self._require(self.SMTP_PASSWORD, "SMTP_PASSWORD")

settings = Settings() # type: ignore[call-arg]