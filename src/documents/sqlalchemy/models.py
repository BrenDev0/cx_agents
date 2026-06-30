from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped


class DocumentRow(Base, TimeStampMixin, IdMixin):
    __tablename__ = "documents"

    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
