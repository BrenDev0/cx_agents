import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String, ForeignKey, Boolean, DateTime

from src.db.sqlalchemy.models import Base, TimeStampMixin, IdMixin
from src.utils import utc_now

class AssistantSettingsRow(Base, IdMixin, TimeStampMixin):
    __tablename__ = "assistant_settings"

    assistant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assistants", ondelete="CASCADE"), nullable=False)
    personality: Mapped[str] = mapped_column(String, nullable=False)
    instructions: Mapped[str] = mapped_column(String, nullable=False)
    rules: Mapped[str] = mapped_column(String, nullable=False)
    has_calendar: Mapped[bool] = mapped_column(Boolean, default=False)
    has_rag: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)