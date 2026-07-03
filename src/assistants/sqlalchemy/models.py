import uuid
from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin


class AssistantRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "assistants"

    user_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    webhook_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    # Only the hash is stored -- the plaintext secret is generated in the usecase,
    # shown once in the response, and never persisted.
    webhook_secret_hash: Mapped[str] = mapped_column(String, nullable=False)

