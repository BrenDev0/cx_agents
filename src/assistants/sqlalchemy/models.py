import uuid
from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin


class AssistantRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "assistants"

    user_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("users", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

