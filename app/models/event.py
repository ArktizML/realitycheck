from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime
from app.models.event_history import EventHistory


class EventStatus(str, enum.Enum):
    planned = "planned"
    done = "done"
    failed = "failed"

class EventAction(str, enum.Enum):
    update_progress = "update_progress"
    mark_done = "mark_done"
    mark_failed = "mark_failed"
    reset_to_planned = "reset_to_planned"

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[EventStatus] = mapped_column(SQLEnum(EventStatus), default=EventStatus.planned)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    failure_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="events")
    history = relationship("EventHistory", back_populates="event", cascade="all, delete-orphan")

