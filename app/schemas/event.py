from pydantic import BaseModel, field_validator
from app.models.event import Title, Expectation, Reality
from datetime import datetime

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


class EventRead(BaseModel):
    id: int
    title: str
    expectation: int
    reality: int
    gap: int
    created_at: datetime

    model_config ={
        "from_attributes": True
    }