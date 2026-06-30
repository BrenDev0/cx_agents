from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin



class UserRow(Base, TimeStampMixin, IdMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String, nullable=False)
    email_hash: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)