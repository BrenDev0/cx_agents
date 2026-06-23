from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, Mapped

from src.utils import utc_now

class Base(DeclarativeBase):
    pass

class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)