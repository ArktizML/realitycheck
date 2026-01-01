from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    expectation: Mapped[int] = mapped_column(Integer, nullable=False)
    reality: Mapped[int] = mapped_column(Integer, nullable=False)
    gap: Mapped[int] = mapped_column(Integer, nullable=False)

Expectation = Annotated[int, Field(ge=0, le=100)]
Reality = Annotated[int, Field(ge=0, le=300)]
Title = Annotated[str, Field(min_length=3, max_length=100)]