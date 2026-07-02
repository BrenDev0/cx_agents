import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, ForeignKey, String, UniqueConstraint
from src.db.sqlalchemy.models import Base, IdMixin, TimeStampMixin


class KnowledgeRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "knowledge"
    __table_args__ = (
        UniqueConstraint("assistant_id", "document_id", name="uq_knowledge_assistant_id_document_id"),
    )

    assistant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)