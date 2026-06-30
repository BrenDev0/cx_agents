from datetime import datetime
import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, UUID
from sqlalchemy.orm import mapped_column, Mapped

from src.utils import utc_now

class Base(DeclarativeBase):
    pass

class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class IdMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)