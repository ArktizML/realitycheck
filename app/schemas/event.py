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

class EventCreate(BaseModel):
    title: Title
    expectation: Expectation
    reality: Reality

    @field_validator("reality")
    @classmethod
    def reality_not_too_extreme(cls, reality, info):
        expectation = info.data.get("expectation")

        if expectation is not None and reality > expectation * 3:
            raise ValueError("Reality is unrealistically higher than expectation.")
        
        return reality

class EventOut(BaseModel):
    id: int
    title: str
    expectation: int
    reality: int
    gap: int

    model_config = {
        "from_attributes": True
    }
