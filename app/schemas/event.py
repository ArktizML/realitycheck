from pydantic import BaseModel, Field, field_validator
from typing_extensions import Annotated

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
