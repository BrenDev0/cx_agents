import uuid 
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, ForeignKey
from src.db.sqlalchemy.models import Base, IdMixin, TimeStampMixin


class KnowledgeRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "knowledge"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)