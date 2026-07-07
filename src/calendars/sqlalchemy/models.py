import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY

from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin
from src.utils import utc_now

class CalendarRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "calendars"

    assistant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False, unique=True)
    calendar_id: Mapped[str | None] = mapped_column(String, nullable=True)
    timezone: Mapped[str | None] = mapped_column(String, nullable=True)
    required_fields: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    title_template: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
