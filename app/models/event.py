from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    expectation: Mapped[int] = mapped_column(Integer, nullable=False)
    reality: Mapped[int] = mapped_column(Integer, nullable=False)
    gap: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="events")


Expectation = Annotated[int, Field(ge=0, le=100)]
Reality = Annotated[int, Field(ge=0, le=300)]
Title = Annotated[str, Field(min_length=3, max_length=100)]