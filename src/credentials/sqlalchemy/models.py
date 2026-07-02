import uuid
from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UUID, String, ForeignKey, DateTime, UniqueConstraint

from src.db.sqlalchemy.models import Base, IdMixin, TimeStampMixin


class IntegrationCredentialRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "integration_credentials"
    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uq_integration_credentials_provider_external_id"),
    )

    assistant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
