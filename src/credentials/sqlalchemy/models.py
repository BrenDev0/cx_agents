import uuid
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import UUID, String

from src.db.sqlalchemy.models import Base, TimeStampMixin


class CredentialRow(Base, TimeStampMixin):
    __tablename__ = "credentials"

    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    acccess_token: Mapped[str] = mapped_column(String, nullable=False)