import uuid
from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin
from sqlalchemy import String, UUID, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, Mapped


class DocumentRow(Base, TimeStampMixin, IdMixin):
    __tablename__ = "documents"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users", ondelete="CASCADE"), nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
