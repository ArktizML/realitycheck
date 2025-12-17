from pydantic import BaseModel

class EventCreate(BaseModel):
    title: str
    expectation: int
    reality: int

class EventOut(BaseModel):
    title: str
    expectation: int
    reality: int
    gap: int
