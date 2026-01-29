from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class EventHistory(Base):
    __tablename__ = "event_history"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    field = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)

    changed_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="history")
