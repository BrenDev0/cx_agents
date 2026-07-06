import uuid
from sqlalchemy import String, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin

class MessagingCredentialRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "messaging_credentials"

    assistant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="Cascade"), nullable=False)
    channel: Mapped[str] = mapped_column(String, nullable=False)
    credential: Mapped[str] = mapped_column(String, nullable=False)